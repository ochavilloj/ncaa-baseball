from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
Base = declarative_base()
engine = create_engine(os.getenv("DB_URL"))

class Player(Base):
    __tablename__ = "players"
    player_id = Column(String, primary_key=True)
    name = Column(String)
    school = Column(String)
    position = Column(String)
    class_year = Column(String)

class BattingStats(Base):
    __tablename__ = "stats_batting"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String)
    season = Column(Integer)
    ab = Column(Integer)
    h = Column(Integer)
    hr = Column(Integer)
    rbi = Column(Integer)
    avg = Column(Float)
    obp = Column(Float)
    slg = Column(Float)

class PitchingStats(Base):
    __tablename__ = "stats_pitching"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String)
    season = Column(Integer)
    era = Column(Float)
    ip = Column(Float)
    k = Column(Integer)
    bb = Column(Integer)
    whip = Column(Float)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables created.")
