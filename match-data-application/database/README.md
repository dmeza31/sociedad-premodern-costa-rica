# Database Schema

This directory contains the PostgreSQL database schema files.

## Files

- `schema.sql` - Complete PostgreSQL database schema for the MTG Match Management system

## Usage

To create the database schema, run:

```bash
psql -U your_username -d your_database -f schema.sql
```

Or from within PostgreSQL:

```sql
\i schema.sql
```

## Schema Overview

The schema includes the following tables:
- `players` - Player information
- `cards` - Magic: The Gathering card data
- `decks` - Deck information
- `deck_cards` - Junction table for deck-card relationships
- `matches` - Match records
- `match_players` - Junction table linking players to matches
- `games` - Individual game results within matches

For detailed documentation, see the main README.md file in the project root.

