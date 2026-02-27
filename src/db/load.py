import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.scrape import scrape_ncaa
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import uuid

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

def clean_batting(df):
    df = df.copy()

    # Drop footer/header rows
    df = df[pd.to_numeric(df["Rk"], errors="coerce").notna()]

    # Clean name — remove *, ?, # (switch hitter/bats indicators)
    df["Name"] = df["Name"].str.replace(r"[*?#]", "", regex=True).str.strip()

    # Rename columns to match our schema
    df = df.rename(columns={
        "Name": "name",
        "G": "g",
        "PA": "pa",
        "AB": "ab",
        "R": "r",
        "H": "h",
        "HR": "hr",
        "RBI": "rbi",
        "BA": "avg",
        "OBP": "obp",
        "SLG": "slg",
        "OPS": "ops"
    })

    # Keep only the columns we need
    cols = ["name", "team", "conference", "g", "pa", "ab", "r", "h", "hr", "rbi", "avg", "obp", "slg", "ops"]
    df = df[[c for c in cols if c in df.columns]]

    # Convert numeric columns
    for col in ["g", "pa", "ab", "r", "h", "hr", "rbi", "avg", "obp", "slg", "ops"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Generate a player_id
    df["player_id"] = df["name"] + "_" + df["team"]
    df["player_id"] = df["player_id"].str.replace(" ", "_").str.lower()
    df["season"] = 2026

    return df.dropna(subset=["name"])

def load_to_db(df):
    # Upsert players
    players = df[["player_id", "name", "team", "conference"]].drop_duplicates("player_id")
    players = players.rename(columns={"team": "school"})

    with engine.begin() as conn:
        for _, row in players.iterrows():
            conn.execute(text("""
                INSERT INTO players (player_id, name, school)
                VALUES (:player_id, :name, :school)
                ON CONFLICT (player_id) DO NOTHING
            """), row.to_dict())

    # Upsert batting stats
    stat_cols = ["player_id", "season", "g", "pa", "ab", "r", "h", "hr", "rbi", "avg", "obp", "slg", "ops"]
    stats = df[[c for c in stat_cols if c in df.columns]].dropna(subset=["player_id"])

    with engine.begin() as conn:
        for _, row in stats.iterrows():
            conn.execute(text("""
                INSERT INTO stats_batting (player_id, season, g, pa, ab, r, h, hr, rbi, avg, obp, slg, ops)
                VALUES (:player_id, :season, :g, :pa, :ab, :r, :h, :hr, :rbi, :avg, :obp, :slg, :ops)
            """), row.to_dict())

    print(f"Loaded {len(players)} players and {len(stats)} batting stat rows.")

if __name__ == "__main__":
    print("Scraping data...")
    #tables = scrape_ncaa(year=2026, max_conferences=2, max_teams=3) changed to get more teams
    tables = scrape_ncaa(year=2026, max_conferences=31, max_teams=999)

    

    all_cleaned = []
    for df in tables:
        try:
            cleaned = clean_batting(df)
            all_cleaned.append(cleaned)
        except Exception as e:
            print(f"Skipping table: {e}")

    if all_cleaned:
        final = pd.concat(all_cleaned, ignore_index=True)
        print(f"Total rows to load: {len(final)}")
        load_to_db(final)
    else:
        print("No data to load.")
