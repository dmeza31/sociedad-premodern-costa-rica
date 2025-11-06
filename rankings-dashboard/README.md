## Tournament Match Results – Streamlit Report

This project provides a Streamlit app (`main.py`) that reads a CSV of tournament match results and produces:
- Player rankings based on total match wins, with bonus points:
  - 2–0 win → +3 points
  - 2–1 win → +1 point
- A deck performance report with match counts, wins, and win rate per deck, plus a bar chart.

### Requirements
- Python 3.8+
- Recommended: create and activate a virtual environment
- Install dependencies (Streamlit, Pandas, Plotly):
  ```bash
  pip install streamlit pandas plotly
  ```

### CSV input
Place your results file at the project root with the name `TournamentMatchResults.csv`.

The app supports CSVs with or without header. If no header is present, the expected column order is:
1. player1
2. player2
3. winner
4. winner_games
5. loser_games
6. deck1
7. deck2

If a header is present, the app will try to map common names to those canonical columns (case-insensitive). Minimum required columns after mapping are:
- `player1`, `player2`, `winner`, `winner_games`, `loser_games`, `deck1`, `deck2`

Example row (no header):
```
DarioRod,DaiH,DarioRod,2,0,Stasis,Psychatog
```

### Scoring and ranking
- Each match contributes to the winner’s totals:
  - +1 match win (used for primary ranking)
  - +3 bonus points if the score was 2–0
  - +1 bonus point if the score was 2–1
- Players are ranked by:
  1) total match wins (desc)
  2) bonus points (desc)
  3) player name (asc)

### Deck win rate
- For each match, the winner’s deck receives +1 win
- Each deck’s matches = total times that deck appears as `deck1` or `deck2`
- Win rate = wins / matches
- The app shows a bar chart of deck win rate and a table with wins/matches

### How to run
From the project directory:
```bash
streamlit run main.py
```
Then open the URL shown in your terminal (usually `http://localhost:8501`).

### Troubleshooting
- File not found: ensure `TournamentMatchResults.csv` is in the same folder as `main.py`
- CSV parse issues: ensure UTF-8 encoding; supported delimiters: comma (default)
- Columns missing: verify that your CSV contains the columns listed in the CSV input section

### Customization
- Adjust scoring logic in `compute_player_standings()` inside `main.py`
- Modify chart style or add filters in the "Deck performance" section
