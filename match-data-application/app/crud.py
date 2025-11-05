"""CRUD operations for database models."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from app.models import (
    Player, Card, Deck, DeckCard, Match, MatchPlayer, Game
)
from app.schemas import (
    PlayerCreate, CardCreate, DeckCreate, DeckCardCreate,
    MatchCreate, GameCreate, MatchPlayerCreate, DeckUpdate, MatchUpdate
)


# Player CRUD
def get_player(db: Session, player_id: int) -> Optional[Player]:
    """Get a player by ID."""
    return db.query(Player).filter(Player.id == player_id).first()


def get_player_by_name(db: Session, name: str) -> Optional[Player]:
    """Get a player by name."""
    return db.query(Player).filter(Player.name == name).first()


def get_players(db: Session, skip: int = 0, limit: int = 100) -> List[Player]:
    """Get all players with pagination."""
    return db.query(Player).offset(skip).limit(limit).all()


def create_player(db: Session, player: PlayerCreate) -> Player:
    """Create a new player."""
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def delete_player(db: Session, player_id: int) -> bool:
    """Delete a player."""
    player = get_player(db, player_id)
    if player:
        db.delete(player)
        db.commit()
        return True
    return False


# Card CRUD
def get_card(db: Session, card_id: int) -> Optional[Card]:
    """Get a card by ID."""
    return db.query(Card).filter(Card.id == card_id).first()


def get_card_by_name(db: Session, name: str, set_code: Optional[str] = None) -> Optional[Card]:
    """Get a card by name and optionally set code."""
    query = db.query(Card).filter(Card.name == name)
    if set_code:
        query = query.filter(Card.set_code == set_code)
    return query.first()


def get_cards(db: Session, skip: int = 0, limit: int = 100) -> List[Card]:
    """Get all cards with pagination."""
    return db.query(Card).offset(skip).limit(limit).all()


def search_cards(db: Session, name: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Card]:
    """Search cards by name (partial match)."""
    query = db.query(Card)
    if name:
        query = query.filter(Card.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()


def create_card(db: Session, card: CardCreate) -> Card:
    """Create a new card."""
    db_card = Card(**card.model_dump())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def delete_card(db: Session, card_id: int) -> bool:
    """Delete a card."""
    card = get_card(db, card_id)
    if card:
        db.delete(card)
        db.commit()
        return True
    return False


# Deck CRUD
def get_deck(db: Session, deck_id: int) -> Optional[Deck]:
    """Get a deck by ID."""
    return db.query(Deck).filter(Deck.id == deck_id).first()


def get_decks(db: Session, skip: int = 0, limit: int = 100) -> List[Deck]:
    """Get all decks with pagination."""
    return db.query(Deck).offset(skip).limit(limit).all()


def create_deck(db: Session, deck: DeckCreate) -> Deck:
    """Create a new deck with cards."""
    deck_data = deck.model_dump(exclude={'cards'})
    db_deck = Deck(**deck_data)
    db.add(db_deck)
    db.flush()  # Get the deck ID
    
    # Add deck cards
    if deck.cards:
        for card_data in deck.cards:
            db_deck_card = DeckCard(deck_id=db_deck.id, **card_data.model_dump())
            db.add(db_deck_card)
    
    db.commit()
    db.refresh(db_deck)
    return db_deck


def update_deck(db: Session, deck_id: int, deck_update: DeckUpdate) -> Optional[Deck]:
    """Update a deck."""
    db_deck = get_deck(db, deck_id)
    if not db_deck:
        return None
    
    update_data = deck_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deck, field, value)
    
    db.commit()
    db.refresh(db_deck)
    return db_deck


def delete_deck(db: Session, deck_id: int) -> bool:
    """Delete a deck."""
    deck = get_deck(db, deck_id)
    if deck:
        db.delete(deck)
        db.commit()
        return True
    return False


def add_card_to_deck(db: Session, deck_id: int, deck_card: DeckCardCreate) -> Optional[DeckCard]:
    """Add a card to a deck."""
    db_deck = get_deck(db, deck_id)
    if not db_deck:
        return None
    
    db_deck_card = DeckCard(deck_id=deck_id, **deck_card.model_dump())
    db.add(db_deck_card)
    db.commit()
    db.refresh(db_deck_card)
    return db_deck_card


def remove_card_from_deck(db: Session, deck_id: int, card_id: int, is_sideboard: bool) -> bool:
    """Remove a card from a deck."""
    deck_card = db.query(DeckCard).filter(
        and_(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card_id,
            DeckCard.is_sideboard == is_sideboard
        )
    ).first()
    
    if deck_card:
        db.delete(deck_card)
        db.commit()
        return True
    return False


def get_decks_by_card(db: Session, card_id: int) -> List[Deck]:
    """Get all decks that contain a specific card."""
    return db.query(Deck).join(DeckCard).filter(DeckCard.card_id == card_id).distinct().all()


# Match CRUD
def get_match(db: Session, match_id: int) -> Optional[Match]:
    """Get a match by ID."""
    return db.query(Match).filter(Match.id == match_id).first()


def get_matches(db: Session, skip: int = 0, limit: int = 100) -> List[Match]:
    """Get all matches with pagination."""
    return db.query(Match).offset(skip).limit(limit).all()


def create_match(db: Session, match: MatchCreate) -> Match:
    """Create a new match with players and games."""
    match_data = match.model_dump(exclude={'players', 'games'})
    db_match = Match(**match_data)
    db.add(db_match)
    db.flush()  # Get the match ID
    
    # Add match players
    for player_data in match.players:
        db_match_player = MatchPlayer(match_id=db_match.id, **player_data.model_dump())
        db.add(db_match_player)
    
    # Add games
    if match.games:
        for game_data in match.games:
            db_game = Game(match_id=db_match.id, **game_data.model_dump())
            db.add(db_game)
    
    db.commit()
    db.refresh(db_match)
    return db_match


def update_match(db: Session, match_id: int, match_update: MatchUpdate) -> Optional[Match]:
    """Update a match."""
    db_match = get_match(db, match_id)
    if not db_match:
        return None
    
    update_data = match_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_match, field, value)
    
    db.commit()
    db.refresh(db_match)
    return db_match


def delete_match(db: Session, match_id: int) -> bool:
    """Delete a match."""
    match = get_match(db, match_id)
    if match:
        db.delete(match)
        db.commit()
        return True
    return False


def add_game_to_match(db: Session, match_id: int, game: GameCreate) -> Optional[Game]:
    """Add a game to a match."""
    db_match = get_match(db, match_id)
    if not db_match:
        return None
    
    db_game = Game(match_id=match_id, **game.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


# Statistics
def get_player_win_stats(db: Session) -> List[dict]:
    """Get win statistics for all players."""
    results = db.query(
        Player.id,
        Player.name,
        func.count(func.distinct(Match.id)).label('matches_won')
    ).join(
        Game, Game.winner_player_id == Player.id
    ).join(
        Match, Match.id == Game.match_id
    ).group_by(
        Player.id, Player.name
    ).all()
    
    return [
        {
            'player_id': r.id,
            'player_name': r.name,
            'matches_won': r.matches_won
        }
        for r in results
    ]


def get_deck_win_rates(db: Session) -> List[dict]:
    """Get win rates between different decks."""
    # Get all matches with exactly 2 different decks
    matches = db.query(Match).join(MatchPlayer).group_by(Match.id).having(
        func.count(func.distinct(MatchPlayer.deck_id)) == 2
    ).all()
    
    deck_stats = {}
    for match in matches:
        match_players = db.query(MatchPlayer).filter(MatchPlayer.match_id == match.id).all()
        if len(match_players) == 2:
            deck1_id = match_players[0].deck_id
            deck2_id = match_players[1].deck_id
            player1_id = match_players[0].player_id
            player2_id = match_players[1].player_id
            
            # Ensure consistent ordering
            if deck1_id > deck2_id:
                deck1_id, deck2_id = deck2_id, deck1_id
                player1_id, player2_id = player2_id, player1_id
            
            key = (deck1_id, deck2_id)
            if key not in deck_stats:
                deck1 = get_deck(db, deck1_id)
                deck2 = get_deck(db, deck2_id)
                deck_stats[key] = {
                    'deck1_id': deck1_id,
                    'deck1_name': deck1.name if deck1 else 'Unknown',
                    'deck2_id': deck2_id,
                    'deck2_name': deck2.name if deck2 else 'Unknown',
                    'deck1_wins': 0,
                    'deck2_wins': 0,
                    'total_matches': 0
                }
            
            # Count wins
            games = db.query(Game).filter(Game.match_id == match.id).all()
            deck1_wins = sum(1 for g in games if g.winner_player_id == player1_id)
            deck2_wins = sum(1 for g in games if g.winner_player_id == player2_id)
            
            if deck1_wins > deck2_wins:
                deck_stats[key]['deck1_wins'] += 1
            elif deck2_wins > deck1_wins:
                deck_stats[key]['deck2_wins'] += 1
            
            deck_stats[key]['total_matches'] += 1
    
    # Calculate win rates
    result_list = []
    for key, stats in deck_stats.items():
        total = stats['total_matches']
        stats['deck1_win_rate'] = round((stats['deck1_wins'] / total * 100) if total > 0 else 0, 2)
        result_list.append(stats)
    
    return result_list


def get_deck_cards(db: Session, deck_id: int) -> List[dict]:
    """Get all cards in a deck."""
    deck_cards = db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()
    return [
        {
            'deck_id': dc.deck_id,
            'deck_name': dc.deck.name,
            'card_id': dc.card_id,
            'card_name': dc.card.name,
            'quantity': dc.quantity,
            'is_sideboard': dc.is_sideboard
        }
        for dc in deck_cards
    ]

