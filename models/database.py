# models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wolfalert.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(100))
    url = Column(String(1000), unique=True)
    published_date = Column(DateTime)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classifications = relationship("Classification", back_populates="article")

class Classification(Base):
    __tablename__ = "classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    industry = Column(String(50))
    impact_level = Column(String(20))  # THREAT, OPPORTUNITY, WATCH, NOISE
    urgency = Column(String(20))       # IMMEDIATE, SHORT_TERM, STRATEGIC
    relevance_score = Column(Float)    # 0-100
    business_functions = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="classifications")
    analysis = relationship("Analysis", back_populates="classification", uselist=False)

class Analysis(Base):
    __tablename__ = "analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    classification_id = Column(Integer, ForeignKey("classifications.id"))
    impact_summary = Column(Text)
    action_recommendations = Column(Text)
    competitive_implications = Column(Text)
    timeline_assessment = Column(Text)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classification = relationship("Classification", back_populates="analysis")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    industry = Column(String(50))
    size = Column(String(20))          # SME, Enterprise, etc.
    functions = Column(Text)           # JSON array
    ai_maturity = Column(String(20))   # BEGINNER, INTERMEDIATE, ADVANCED
    created_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")