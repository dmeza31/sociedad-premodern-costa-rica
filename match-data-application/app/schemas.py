"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Player Schemas
class PlayerBase(BaseModel):
    name: str = Field(..., max_length=255)


class PlayerCreate(PlayerBase):
    pass


class Player(PlayerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Card Schemas
class CardBase(BaseModel):
    name: str = Field(..., max_length=255)
    mana_cost: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = Field(None, max_length=100)
    rarity: Optional[str] = Field(None, max_length=50)
    set_code: Optional[str] = Field(None, max_length=10)


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Deck Schemas
class DeckCardBase(BaseModel):
    card_id: int
    quantity: int = Field(1, gt=0)
    is_sideboard: bool = False


class DeckCardCreate(DeckCardBase):
    pass


class DeckCard(DeckCardBase):
    id: int
    deck_id: int
    created_at: datetime
    card: Optional[Card] = None

    class Config:
        from_attributes = True


class DeckBase(BaseModel):
    name: str = Field(..., max_length=255)
    format: str = Field(..., max_length=50)
    description: Optional[str] = None


class DeckCreate(DeckBase):
    cards: Optional[List[DeckCardCreate]] = []


class Deck(DeckBase):
    id: int
    created_at: datetime
    deck_cards: Optional[List[DeckCard]] = []

    class Config:
        from_attributes = True


class DeckUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    format: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


# Match Schemas
class MatchPlayerBase(BaseModel):
    player_id: int
    deck_id: int


class MatchPlayerCreate(MatchPlayerBase):
    pass


class MatchPlayer(MatchPlayerBase):
    id: int
    match_id: int
    created_at: datetime
    player: Optional[Player] = None
    deck: Optional[Deck] = None

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    game_number: int = Field(..., ge=1, le=3)
    winner_player_id: int


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: int
    match_id: int
    created_at: datetime
    winner: Optional[Player] = None

    class Config:
        from_attributes = True


class MatchBase(BaseModel):
    date: Optional[datetime] = None
    format: str = Field(..., max_length=50)
    notes: Optional[str] = None


class MatchCreate(MatchBase):
    players: List[MatchPlayerCreate] = Field(..., min_items=2, max_items=2)
    games: Optional[List[GameCreate]] = []


class Match(MatchBase):
    id: int
    created_at: datetime
    match_players: Optional[List[MatchPlayer]] = []
    games: Optional[List[Game]] = []

    class Config:
        from_attributes = True


class MatchUpdate(BaseModel):
    date: Optional[datetime] = None
    format: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


# Statistics Schemas
class PlayerWinStats(BaseModel):
    player_id: int
    player_name: str
    matches_won: int


class DeckWinRate(BaseModel):
    deck1_id: int
    deck1_name: str
    deck2_id: int
    deck2_name: str
    deck1_wins: int
    deck2_wins: int
    total_matches: int
    deck1_win_rate: Optional[float] = None


class DeckCardInfo(BaseModel):
    deck_id: int
    deck_name: str
    card_id: int
    card_name: str
    quantity: int
    is_sideboard: bool

