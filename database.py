'''
    CSCI - 622 - Data Security & Privacy
    Project Phase 2 - database.py
    Authors: Samuel Roberts (svr9047) & Lianna Pottgen (lrp2755)

    This file just simply creates the sqlite database!
'''
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = "LiannaPottgen"
DB_PASS = "Test1234!"
DB_HOST = "ritfinanceserver622.postgres.database.azure.com"
DB_PORT = "5432"
DB_NAME = "financedb"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

engine = create_engine(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✅ Connected successfully:", result.scalar())
    except Exception as e:
        print("❌ Connection failed:", e)
