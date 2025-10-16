'''
    CSCI - 622 - Data Security & Privacy
    Project Phase 2 - database.py
    Authors: Samuel Roberts (svr9047) & Lianna Pottgen (lrp2755)

    This file just simply creates the sqlite database!
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///fake_investing.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
