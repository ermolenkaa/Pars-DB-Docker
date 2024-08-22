from sqlalchemy import TIMESTAMP, Column, Date, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    date = Column(Date)
    time = Column(String)
    title = Column(String)
    text = Column(Text)
