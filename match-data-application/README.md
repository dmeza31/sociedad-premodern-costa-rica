# Magic: The Gathering Match Management Application

This application is designed to manage Magic: The Gathering match data, including players, decks, cards, and match results.

## Project Structure

```
.
├── app/                 # Python application code
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas for request/response
│   ├── crud.py          # CRUD operations for database models
│   └── database.py      # Database connection and session management
├── database/            # PostgreSQL database files
│   └── schema.sql       # PostgreSQL database schema
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables example
├── .gitignore          # Git ignore patterns
└── README.md            # This file
```

## Database Schema Diagram

```
┌─────────────┐
│   players   │
├─────────────┤
│ id (PK)     │
│ name        │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────┐
│ match_players   │
├─────────────────┤
│ id (PK)         │
│ match_id (FK)   │──┐
│ player_id (FK)  │  │
│ deck_id (FK)    │──┼──┐
└─────────────────┘  │  │
                     │  │
                     │  │
┌─────────────┐      │  │    ┌─────────────┐
│   matches   │      │  │    │    decks    │
├─────────────┤      │  │    ├─────────────┤
│ id (PK)     │◄─────┘  │    │ id (PK)     │
│ date        │         │    │ name        │
│ format      │         │    │ format      │
│ notes       │         │    │ description │
│ created_at  │         │    │ created_at  │
└──────┬──────┘         │    └──────┬──────┘
       │                │           │
       │ 1:N            │           │ 1:N
       │                │           │
       ▼                │           ▼
┌─────────────┐         │    ┌──────────────┐
│    games    │         │    │ deck_cards   │
├─────────────┤         │    ├──────────────┤
│ id (PK)     │         │    │ id (PK)      │
│ match_id    │         │    │ deck_id (FK) │◄──┐
│ game_number │         │    │ card_id (FK) │   │
│ winner_     │         │    │ quantity     │   │
│   player_id │         │    │ is_sideboard │   │
│ created_at  │         │    └──────────────┘   │
└─────────────┘         │                       │
                        │                       │
                        │                       │
                        │              ┌─────────────┐
                        │              │    cards    │
                        │              ├─────────────┤
                        │              │ id (PK)     │
                        │              │ name        │
                        │              │ mana_cost   │
                        │              │ type        │
                        │              │ rarity      │
                        │              │ set_code    │
                        │              │ created_at  │
                        │              └─────────────┘
                        │
                        └──────────────────┘
```

## Table Descriptions

### `players`
Stores information about players who participate in matches.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each player
- `name` (VARCHAR(255)): Player's name (unique)
- `created_at` (TIMESTAMP): When the player record was created

**Use Cases:**
- Track player participation in matches
- Calculate player win statistics

---

### `cards`
Stores information about Magic: The Gathering cards.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each card
- `name` (VARCHAR(255)): Card name
- `mana_cost` (VARCHAR(50)): Mana cost (e.g., "1R", "2UU")
- `type` (VARCHAR(100)): Card type (e.g., "Creature", "Instant", "Sorcery")
- `rarity` (VARCHAR(50)): Card rarity (e.g., "Common", "Uncommon", "Rare", "Mythic")
- `set_code` (VARCHAR(10)): Set code (e.g., "MH2", "MH3")
- `created_at` (TIMESTAMP): When the card record was created

**Note:** The combination of `name` and `set_code` must be unique to handle reprints.

**Use Cases:**
- Query decks by specific cards
- Track card usage across different decks

---

### `decks`
Stores information about decks used in matches.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each deck
- `name` (VARCHAR(255)): Deck name
- `format` (VARCHAR(50)): Format name (e.g., "Premodern", "Modern", "Legacy")
- `description` (TEXT): Optional deck description
- `created_at` (TIMESTAMP): When the deck record was created

**Use Cases:**
- Track deck performance
- Calculate win rates between different decks

---

### `deck_cards`
Junction table that links decks to cards (many-to-many relationship).

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each deck-card relationship
- `deck_id` (INTEGER FK): References `decks.id`
- `card_id` (INTEGER FK): References `cards.id`
- `quantity` (INTEGER): Number of copies of this card in the deck (default: 1)
- `is_sideboard` (BOOLEAN): Whether this card is in the sideboard (default: FALSE)
- `created_at` (TIMESTAMP): When the relationship was created

**Constraints:**
- The combination of `deck_id`, `card_id`, and `is_sideboard` must be unique
- `quantity` must be greater than 0

**Use Cases:**
- Store complete decklists
- Query decks by cards they contain
- Distinguish between mainboard and sideboard cards

---

### `matches`
Stores information about match records.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each match
- `date` (TIMESTAMP): When the match took place
- `format` (VARCHAR(50)): Format name (e.g., "Premodern", "Modern")
- `notes` (TEXT): Optional match notes
- `created_at` (TIMESTAMP): When the match record was created

**Use Cases:**
- Track match history
- Organize matches by date and format

---

### `match_players`
Junction table that links players to matches and tracks which deck each player used.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier
- `match_id` (INTEGER FK): References `matches.id`
- `player_id` (INTEGER FK): References `players.id`
- `deck_id` (INTEGER FK): References `decks.id`
- `created_at` (TIMESTAMP): When the relationship was created

**Constraints:**
- The combination of `match_id` and `player_id` must be unique (each player can only appear once per match)

**Use Cases:**
- Link players to matches
- Track which deck each player used in each match
- Enable queries about deck performance

---

### `games`
Stores individual game results within matches. Matches are best-of-3, so each match can have up to 3 games.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier for each game
- `match_id` (INTEGER FK): References `matches.id`
- `game_number` (INTEGER): Game number within the match (1, 2, or 3)
- `winner_player_id` (INTEGER FK): References `players.id` - the player who won this game
- `created_at` (TIMESTAMP): When the game record was created

**Constraints:**
- `game_number` must be between 1 and 3
- The combination of `match_id` and `game_number` must be unique

**Use Cases:**
- Track individual game results
- Determine match winners (first player to win 2 games)
- Calculate detailed statistics

---

## Example Queries

### How many matches has a player won?
```sql
SELECT 
    p.name,
    COUNT(DISTINCT m.id) as matches_won
FROM players p
JOIN games g ON g.winner_player_id = p.id
JOIN matches m ON m.id = g.match_id
GROUP BY p.id, p.name;
```

### Win rate between different decks
```sql
SELECT 
    d1.name as deck1_name,
    d2.name as deck2_name,
    COUNT(DISTINCT CASE WHEN g.winner_player_id = mp1.player_id THEN m.id END) as deck1_wins,
    COUNT(DISTINCT CASE WHEN g.winner_player_id = mp2.player_id THEN m.id END) as deck2_wins,
    COUNT(DISTINCT m.id) as total_matches,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN g.winner_player_id = mp1.player_id THEN m.id END) / 
        NULLIF(COUNT(DISTINCT m.id), 0), 
        2
    ) as deck1_win_rate
FROM matches m
JOIN match_players mp1 ON mp1.match_id = m.id
JOIN match_players mp2 ON mp2.match_id = m.id AND mp2.player_id != mp1.player_id
JOIN decks d1 ON d1.id = mp1.deck_id
JOIN decks d2 ON d2.id = mp2.deck_id
JOIN games g ON g.match_id = m.id
WHERE d1.id < d2.id  -- Avoid duplicate pairs
GROUP BY d1.id, d1.name, d2.id, d2.name;
```

### What cards are in different decks?
```sql
SELECT 
    d.name as deck_name,
    c.name as card_name,
    dc.quantity,
    dc.is_sideboard
FROM decks d
JOIN deck_cards dc ON dc.deck_id = d.id
JOIN cards c ON c.id = dc.card_id
WHERE d.name = 'Your Deck Name'
ORDER BY dc.is_sideboard, c.name;
```

### Find decks containing a specific card
```sql
SELECT DISTINCT
    d.name as deck_name,
    dc.quantity,
    dc.is_sideboard
FROM decks d
JOIN deck_cards dc ON dc.deck_id = d.id
JOIN cards c ON c.id = dc.card_id
WHERE c.name = 'Lightning Bolt'
ORDER BY d.name;
```

## Installation

To create the database schema, run:

```bash
psql -U your_username -d your_database -f database/schema.sql
```

Or from within PostgreSQL:

```sql
\i database/schema.sql
```

## Notes

- The schema uses CASCADE deletes for referential integrity
- Indexes are created on foreign keys and frequently queried columns for performance
- The schema supports distinguishing between mainboard and sideboard cards
- Match results are tracked at the game level, allowing for best-of-3 format tracking

---

# RESTful API

This project includes a FastAPI-based RESTful API for interacting with the database.

## API Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `env_example.txt` to `.env`
   - Update the `DATABASE_URL` with your PostgreSQL connection details:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/database_name
     ```

3. **Create the database tables:**
   The API will automatically create tables when first run, or you can run the SQL schema manually:
   ```bash
   psql -U your_username -d your_database -f database/schema.sql
   ```

4. **Run the API server:**
   ```bash
   python -m app.main
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API documentation:**
   - Interactive API docs (Swagger UI): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Players

- `POST /players` - Create a new player
- `GET /players` - Get all players (with pagination)
- `GET /players/{player_id}` - Get a player by ID
- `DELETE /players/{player_id}` - Delete a player

### Cards

- `POST /cards` - Create a new card
- `GET /cards` - Get all cards (with pagination and optional name search)
- `GET /cards/{card_id}` - Get a card by ID
- `DELETE /cards/{card_id}` - Delete a card

### Decks

- `POST /decks` - Create a new deck (with optional cards)
- `GET /decks` - Get all decks (with pagination)
- `GET /decks/{deck_id}` - Get a deck by ID
- `PUT /decks/{deck_id}` - Update a deck
- `DELETE /decks/{deck_id}` - Delete a deck
- `POST /decks/{deck_id}/cards` - Add a card to a deck
- `DELETE /decks/{deck_id}/cards/{card_id}` - Remove a card from a deck
- `GET /decks/{deck_id}/cards` - Get all cards in a deck
- `GET /cards/{card_id}/decks` - Get all decks containing a specific card

### Matches

- `POST /matches` - Create a new match (with players and optional games)
- `GET /matches` - Get all matches (with pagination)
- `GET /matches/{match_id}` - Get a match by ID
- `PUT /matches/{match_id}` - Update a match
- `DELETE /matches/{match_id}` - Delete a match
- `POST /matches/{match_id}/games` - Add a game to a match

### Statistics

- `GET /stats/players/wins` - Get win statistics for all players
- `GET /stats/decks/win-rates` - Get win rates between different decks

## Example API Usage

### Create a Player
```bash
curl -X POST "http://localhost:8000/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

### Create a Card
```bash
curl -X POST "http://localhost:8000/cards" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lightning Bolt",
    "mana_cost": "R",
    "type": "Instant",
    "rarity": "Common",
    "set_code": "MH2"
  }'
```

### Create a Deck with Cards
```bash
curl -X POST "http://localhost:8000/decks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Burn",
    "format": "Premodern",
    "description": "Aggressive red deck",
    "cards": [
      {
        "card_id": 1,
        "quantity": 4,
        "is_sideboard": false
      }
    ]
  }'
```

### Create a Match
```bash
curl -X POST "http://localhost:8000/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "Premodern",
    "players": [
      {"player_id": 1, "deck_id": 1},
      {"player_id": 2, "deck_id": 2}
    ],
    "games": [
      {
        "game_number": 1,
        "winner_player_id": 1
      },
      {
        "game_number": 2,
        "winner_player_id": 1
      }
    ]
  }'
```

### Get Player Win Statistics
```bash
curl -X GET "http://localhost:8000/stats/players/wins"
```

### Get Deck Win Rates
```bash
curl -X GET "http://localhost:8000/stats/decks/win-rates"
```

## API Features

- **Automatic Documentation**: FastAPI generates interactive API documentation at `/docs`
- **Request Validation**: All requests are validated using Pydantic schemas
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **CORS Support**: CORS middleware enabled for cross-origin requests
- **Pagination**: Most list endpoints support pagination with `skip` and `limit` parameters
- **Search**: Card endpoints support search by name


