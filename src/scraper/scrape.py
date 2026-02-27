import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
BASE_URL = "https://www.baseball-reference.com"

# def get_soup(url):
#     time.sleep(4)  # respectful delay to avoid getting blocked
#     resp = requests.get(url, headers=HEADERS)
#     if resp.status_code != 200:
#         print(f"Failed to fetch {url} — status {resp.status_code}")
#         return None
#     return BeautifulSoup(resp.text, "html.parser")

def get_soup(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(4)
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
            elif resp.status_code == 429:
                print(f"Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                print(f"Failed {url} — status {resp.status_code}")
                return None
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(10)
    return None

def get_ncaa_conferences(year=2026):
    url = f"{BASE_URL}/register/league.cgi?year={year}"
    soup = get_soup(url)
    if not soup:
        return []

    conferences = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/register/league.cgi?id=" in href:
            conferences.append({
                "name": link.text.strip(),
                "url": BASE_URL + href
            })
    print(f"Found {len(conferences)} conferences")
    return conferences

def get_teams_from_conference(conf_url):
    soup = get_soup(conf_url)
    if not soup:
        return []

    teams = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/register/team.cgi?id=" in href:
            teams.append({
                "name": link.text.strip(),
                "url": BASE_URL + href
            })
    return teams

def get_players_from_team(team_url):
    soup = get_soup(team_url)
    if not soup:
        return pd.DataFrame()

    tables = soup.find_all("table")
    if not tables:
        return pd.DataFrame()

    dfs = []
    for table in tables:
        try:
            df = pd.read_html(str(table))[0]
            dfs.append(df)
        except Exception:
            continue

    return dfs

def scrape_ncaa(year=2026, max_conferences=2, max_teams=3):
    all_data = []

    conferences = get_ncaa_conferences(year)[:max_conferences]

    for conf in conferences:
        print(f"\nConference: {conf['name']}")
        teams = get_teams_from_conference(conf["url"])[:max_teams]

        for team in teams:
            print(f"  Team: {team['name']}")
            dfs = get_players_from_team(team["url"])
            for df in dfs:
                df["team"] = team["name"]
                df["conference"] = conf["name"]
                all_data.append(df)

    return all_data

if __name__ == "__main__":
    results = scrape_ncaa(year=2026, max_conferences=2, max_teams=3)
    for i, df in enumerate(results):
        print(f"\n--- Table {i+1} ---")
        print(df.head())
