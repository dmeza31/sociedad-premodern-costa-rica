"""FastAPI application for MTG Match Management."""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, engine, Base
from app.models import Player, Card, Deck, Match, MatchPlayer, Game
from app import crud
from app.schemas import (
    PlayerCreate, Player as PlayerSchema,
    CardCreate, Card as CardSchema,
    DeckCreate, Deck as DeckSchema, DeckUpdate,
    MatchCreate, Match as MatchSchema, MatchUpdate,
    GameCreate, Game as GameSchema,
    DeckCardCreate, DeckCard as DeckCardSchema,
    PlayerWinStats, DeckWinRate, DeckCardInfo
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MTG Match Management API",
    description="RESTful API for managing Magic: The Gathering match data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "MTG Match Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Player endpoints
@app.post("/players", response_model=PlayerSchema, status_code=status.HTTP_201_CREATED)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Create a new player."""
    # Check if player already exists
    existing = crud.get_player_by_name(db, player.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player with name '{player.name}' already exists"
        )
    return crud.create_player(db, player)


@app.get("/players", response_model=List[PlayerSchema])
def read_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all players with pagination."""
    return crud.get_players(db, skip=skip, limit=limit)


@app.get("/players/{player_id}", response_model=PlayerSchema)
def read_player(player_id: int, db: Session = Depends(get_db)):
    """Get a player by ID."""
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found"
        )
    return player


@app.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Delete a player."""
    if not crud.delete_player(db, player_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found"
        )


# Card endpoints
@app.post("/cards", response_model=CardSchema, status_code=status.HTTP_201_CREATED)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """Create a new card."""
    return crud.create_card(db, card)


@app.get("/cards", response_model=List[CardSchema])
def read_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all cards with optional search by name."""
    if name:
        return crud.search_cards(db, name=name, skip=skip, limit=limit)
    return crud.get_cards(db, skip=skip, limit=limit)


@app.get("/cards/{card_id}", response_model=CardSchema)
def read_card(card_id: int, db: Session = Depends(get_db)):
    """Get a card by ID."""
    card = crud.get_card(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found"
        )
    return card


@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    """Delete a card."""
    if not crud.delete_card(db, card_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found"
        )


# Deck endpoints
@app.post("/decks", response_model=DeckSchema, status_code=status.HTTP_201_CREATED)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    """Create a new deck with optional cards."""
    return crud.create_deck(db, deck)


@app.get("/decks", response_model=List[DeckSchema])
def read_decks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all decks with pagination."""
    return crud.get_decks(db, skip=skip, limit=limit)


@app.get("/decks/{deck_id}", response_model=DeckSchema)
def read_deck(deck_id: int, db: Session = Depends(get_db)):
    """Get a deck by ID."""
    deck = crud.get_deck(db, deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return deck


@app.put("/decks/{deck_id}", response_model=DeckSchema)
def update_deck(deck_id: int, deck_update: DeckUpdate, db: Session = Depends(get_db)):
    """Update a deck."""
    deck = crud.update_deck(db, deck_id, deck_update)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return deck


@app.delete("/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    """Delete a deck."""
    if not crud.delete_deck(db, deck_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )


@app.post("/decks/{deck_id}/cards", response_model=DeckCardSchema, status_code=status.HTTP_201_CREATED)
def add_card_to_deck(deck_id: int, deck_card: DeckCardCreate, db: Session = Depends(get_db)):
    """Add a card to a deck."""
    deck_card = crud.add_card_to_deck(db, deck_id, deck_card)
    if not deck_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return deck_card


@app.delete("/decks/{deck_id}/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card_from_deck(
    deck_id: int,
    card_id: int,
    is_sideboard: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Remove a card from a deck."""
    if not crud.remove_card_from_deck(db, deck_id, card_id, is_sideboard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck card not found"
        )


@app.get("/decks/{deck_id}/cards", response_model=List[DeckCardInfo])
def get_deck_cards(deck_id: int, db: Session = Depends(get_db)):
    """Get all cards in a deck."""
    deck = crud.get_deck(db, deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return crud.get_deck_cards(db, deck_id)


@app.get("/cards/{card_id}/decks", response_model=List[DeckSchema])
def get_decks_by_card(card_id: int, db: Session = Depends(get_db)):
    """Get all decks that contain a specific card."""
    card = crud.get_card(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found"
        )
    return crud.get_decks_by_card(db, card_id)


# Match endpoints
@app.post("/matches", response_model=MatchSchema, status_code=status.HTTP_201_CREATED)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """Create a new match with players and optional games."""
    # Validate that exactly 2 players are provided
    if len(match.players) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A match must have exactly 2 players"
        )
    
    # Validate that players are different
    if match.players[0].player_id == match.players[1].player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A match must have 2 different players"
        )
    
    # Validate players exist
    for mp in match.players:
        player = crud.get_player(db, mp.player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {mp.player_id} not found"
            )
        deck = crud.get_deck(db, mp.deck_id)
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck with ID {mp.deck_id} not found"
            )
    
    # Validate games
    if match.games:
        for game in match.games:
            if game.game_number < 1 or game.game_number > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Game number must be between 1 and 3"
                )
            # Check if winner is one of the players
            winner_ids = [mp.player_id for mp in match.players]
            if game.winner_player_id not in winner_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Game winner must be one of the match players"
                )
    
    return crud.create_match(db, match)


@app.get("/matches", response_model=List[MatchSchema])
def read_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all matches with pagination."""
    return crud.get_matches(db, skip=skip, limit=limit)


@app.get("/matches/{match_id}", response_model=MatchSchema)
def read_match(match_id: int, db: Session = Depends(get_db)):
    """Get a match by ID."""
    match = crud.get_match(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    return match


@app.put("/matches/{match_id}", response_model=MatchSchema)
def update_match(match_id: int, match_update: MatchUpdate, db: Session = Depends(get_db)):
    """Update a match."""
    match = crud.update_match(db, match_id, match_update)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    return match


@app.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    """Delete a match."""
    if not crud.delete_match(db, match_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )


@app.post("/matches/{match_id}/games", response_model=GameSchema, status_code=status.HTTP_201_CREATED)
def add_game_to_match(match_id: int, game: GameCreate, db: Session = Depends(get_db)):
    """Add a game to a match."""
    match = crud.get_match(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    
    # Validate game number
    if game.game_number < 1 or game.game_number > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game number must be between 1 and 3"
        )
    
    # Check if game number already exists
    existing_game = db.query(Game).filter(
        Game.match_id == match_id,
        Game.game_number == game.game_number
    ).first()
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game {game.game_number} already exists for this match"
        )
    
    # Validate winner is one of the match players
    match_players = db.query(MatchPlayer).filter(MatchPlayer.match_id == match_id).all()
    winner_ids = [mp.player_id for mp in match_players]
    if game.winner_player_id not in winner_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game winner must be one of the match players"
        )
    
    return crud.add_game_to_match(db, match_id, game)


# Statistics endpoints
@app.get("/stats/players/wins", response_model=List[PlayerWinStats])
def get_player_win_stats(db: Session = Depends(get_db)):
    """Get win statistics for all players."""
    return crud.get_player_win_stats(db)


@app.get("/stats/decks/win-rates", response_model=List[DeckWinRate])
def get_deck_win_rates(db: Session = Depends(get_db)):
    """Get win rates between different decks."""
    return crud.get_deck_win_rates(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

