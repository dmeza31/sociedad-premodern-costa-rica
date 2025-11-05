"""SQLAlchemy models for the MTG Match Management database."""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Player(Base):
    """Player model."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    match_players = relationship("MatchPlayer", back_populates="player", cascade="all, delete-orphan")
    games_won = relationship("Game", foreign_keys="Game.winner_player_id", back_populates="winner")


class Card(Base):
    """Card model."""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    mana_cost = Column(String(50))
    type = Column(String(100))
    rarity = Column(String(50))
    set_code = Column(String(10))
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('name', 'set_code', name='unique_card_name_set'),
    )

    # Relationships
    deck_cards = relationship("DeckCard", back_populates="card", cascade="all, delete-orphan")


class Deck(Base):
    """Deck model."""
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    format = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    deck_cards = relationship("DeckCard", back_populates="deck", cascade="all, delete-orphan")
    match_players = relationship("MatchPlayer", back_populates="deck", cascade="all, delete-orphan")


class DeckCard(Base):
    """Deck-Card junction table."""
    __tablename__ = "deck_cards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    is_sideboard = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('deck_id', 'card_id', 'is_sideboard', name='unique_deck_card_sideboard'),
        CheckConstraint('quantity > 0', name='positive_quantity'),
    )

    # Relationships
    deck = relationship("Deck", back_populates="deck_cards")
    card = relationship("Card", back_populates="deck_cards")


class Match(Base):
    """Match model."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    format = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    match_players = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="match", cascade="all, delete-orphan")


class MatchPlayer(Base):
    """Match-Player junction table."""
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('match_id', 'player_id', name='unique_match_player'),
    )

    # Relationships
    match = relationship("Match", back_populates="match_players")
    player = relationship("Player", back_populates="match_players")
    deck = relationship("Deck", back_populates="match_players")


class Game(Base):
    """Game model (individual games within a match)."""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    game_number = Column(Integer, nullable=False)
    winner_player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('match_id', 'game_number', name='unique_match_game'),
        CheckConstraint('game_number >= 1 AND game_number <= 3', name='valid_game_number'),
    )

    # Relationships
    match = relationship("Match", back_populates="games")
    winner = relationship("Player", foreign_keys=[winner_player_id], back_populates="games_won")

