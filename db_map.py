from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Dotabaff_db(Base):
    __tablename__ = 'Media ids'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(255))
    dotabuff = Column(String(255))
