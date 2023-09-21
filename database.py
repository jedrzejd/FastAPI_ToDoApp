from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/ToDoApplicationDatabase'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@localhost/ToDoApplicationDatabase'
SQLALCHEMY_DATABASE_URI = 'sqlite:///./ToDoApplicationDatabase.db'

engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()