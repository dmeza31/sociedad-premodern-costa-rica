import os
from typing import Optional

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Tournament Report", page_icon="📊", layout="wide")

CSV_FILE = "TournamentMatchResults.csv"


@st.cache_data(ttl=30)
def load_results_csv(path: str) -> pd.DataFrame:
    """Load tournament match results from CSV.

    Accepts files with or without header. Expected columns if no header:
    player1, player2, winner, winner_games, loser_games, deck1, deck2
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    # Try default read
    df = pd.read_csv(path, encoding="utf-8-sig", header=0)

    # If header seems missing or not useful, assign expected names
    if df.shape[1] >= 7 and not set(["winner", "winner_games", "loser_games"]).issubset(set(c.lower() for c in df.columns)):
        df = pd.read_csv(path, encoding="utf-8-sig", header=None)
        df = df.iloc[:, :7]
        df.columns = [
            "player1",
            "player2",
            "winner",
            "winner_games",
            "loser_games",
            "deck1",
            "deck2",
        ]
    else:
        # Normalize likely column labels to canonical names
        rename_map = {}
        cols_lower = {c.lower(): c for c in df.columns}
        def find(*keys: str) -> Optional[str]:
            for k in keys:
                if k in cols_lower:
                    return cols_lower[k]
            return None
        if find("player1"): rename_map[find("player1")] = "player1"
        if find("player2"): rename_map[find("player2")] = "player2"
        if find("winner"): rename_map[find("winner")] = "winner"
        if find("winner_games", "winnergames", "wg"): rename_map[find("winner_games", "winnergames", "wg")] = "winner_games"
        if find("loser_games", "losergames", "lg"): rename_map[find("loser_games", "losergames", "lg")] = "loser_games"
        if find("deck1"): rename_map[find("deck1")] = "deck1"
        if find("deck2"): rename_map[find("deck2")] = "deck2"
        df = df.rename(columns=rename_map)

    # Ensure required columns
    required = ["player1", "player2", "winner", "winner_games", "loser_games", "deck1", "deck2"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {missing}")

    # Types
    df["winner_games"] = pd.to_numeric(df["winner_games"], errors="coerce").fillna(0).astype(int)
    df["loser_games"] = pd.to_numeric(df["loser_games"], errors="coerce").fillna(0).astype(int)

    # Clean strings
    for col in ["player1", "player2", "winner", "deck1", "deck2"]:
        df[col] = df[col].astype(str).str.strip()

    return df


def compute_player_standings(results: pd.DataFrame) -> pd.DataFrame:
    # Points: 3 for 2-0, 1 for 2-1, else 0
    def points(row: pd.Series) -> int:
        if row["winner_games"] == 2 and row["loser_games"] == 0:
            return 3
        if row["winner_games"] == 2 and row["loser_games"] == 1:
            return 1
        return 0

    tmp = results.copy()
    tmp["points"] = tmp.apply(points, axis=1)

    wins_by_player = tmp.groupby("winner").size().rename("wins").reset_index()
    points_by_player = tmp.groupby("winner")["points"].sum().rename("points").reset_index()

    standings = pd.merge(wins_by_player, points_by_player, on="winner", how="outer").fillna(0)
    standings["wins"] = standings["wins"].astype(int)
    standings["points"] = standings["points"].astype(int)

    standings = standings.sort_values(["wins", "points", "winner"], ascending=[False, False, True]).reset_index(drop=True)
    standings = standings.rename(columns={"winner": "player"})
    return standings


def compute_deck_win_rates(results: pd.DataFrame) -> pd.DataFrame:
    # Determine winning and losing decks per match
    win_deck = results.apply(lambda r: r["deck1"] if r["winner"] == r["player1"] else r["deck2"], axis=1)
    lose_deck = results.apply(lambda r: r["deck2"] if r["winner"] == r["player1"] else r["deck1"], axis=1)

    decks_played = pd.concat([results["deck1"], results["deck2"]], ignore_index=True)
    matches_played = decks_played.value_counts().rename_axis("deck").rename("matches")

    deck_wins = win_deck.value_counts().rename_axis("deck").rename("wins")

    perf = pd.concat([matches_played, deck_wins], axis=1).fillna(0)
    perf["wins"] = perf["wins"].astype(int)
    perf["matches"] = perf["matches"].astype(int)
    perf["win_rate"] = (perf["wins"] / perf["matches"]).fillna(0.0)
    perf = perf.sort_values(["win_rate", "wins"], ascending=[False, False]).reset_index()
    return perf


# Header
st.markdown("# 📊 Tournament Report")
st.caption("Ranking por victorias (tabla y gráfico simples) y win rate por mazo.")

# Load data
try:
    results_df = load_results_csv(CSV_FILE)
except Exception as exc:
    st.error("No se pudo cargar el CSV de resultados.")
    st.exception(exc)
    st.stop()

# Standings (simplified with points = wins * 3)
st.subheader("Clasificación de Jugadores (simple)")
standings_full = compute_player_standings(results_df)
standings_simple = standings_full[["player", "wins"]].copy()
standings_simple["points"] = standings_simple["wins"] * 3
standings_simple = standings_simple.sort_values(["wins", "player"], ascending=[False, True]).reset_index(drop=True)
st.dataframe(standings_simple, use_container_width=True, hide_index=True)

# Simple ranking chart (player vs wins)
fig_rank = px.bar(standings_simple, x="player", y="wins", title="Ranking por número de victorias")
fig_rank.update_layout(xaxis_tickangle=-35, yaxis_title="Victorias")
st.plotly_chart(fig_rank, use_container_width=True)

# Deck performance
st.subheader("Rendimiento por Mazo (Win Rate)")
deck_perf_df = compute_deck_win_rates(results_df)
col1, col2 = st.columns([0.6, 0.4])
with col1:
    fig = px.bar(
        deck_perf_df,
        x="deck",
        y="win_rate",
        hover_data=["wins", "matches"],
        text=(deck_perf_df["win_rate"] * 100).round(1).astype(str) + "%",
        title="Win Rate por Mazo",
    )
    fig.update_layout(xaxis_tickangle=-35, yaxis_title="Win Rate")
    fig.update_yaxes(tickformat=",.0%", rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.dataframe(
        deck_perf_df.rename(
            columns={"deck": "Mazo", "wins": "Victorias", "matches": "Partidos", "win_rate": "Win Rate"}
        ),
        use_container_width=True,
        hide_index=True,
    )

# Sidebar
with st.sidebar:
    st.header("Datos")
    st.caption(f"Fuente: {CSV_FILE}")
    if st.button("Recargar datos"):
        load_results_csv.clear()
        st.rerun()
