# NCAA Baseball Analytics Pipeline

A full end-to-end data engineering and analytics project scraping NCAA baseball 
player statistics from Baseball Reference.

## Stack
- **Scraping**: Python, Requests, BeautifulSoup
- **Data Engineering**: Pandas, SQLAlchemy
- **Database**: PostgreSQL
- **Dashboard**: Streamlit, Plotly

## Features
- Scrapes batting and pitching stats for all 31 NCAA conferences
- Stores 3,000+ players in a PostgreSQL database
- Interactive Streamlit dashboard with filters by conference, school, and at bats

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/db/models.py
python src/db/load.py
streamlit run dashboard/app.py
```

## Project Structure
```
ncaa-baseball/
├── src/
│   ├── scraper/scrape.py      # Web scraping logic
│   ├── db/models.py           # Database schema
│   └── db/load.py             # ETL pipeline
└── dashboard/app.py           # Streamlit dashboard
```
