import os
DB_URL = os.getenv("DATABASE_URL")

if __name__ == '__Real_estate__':
    Real_estate.run()


#property listing
 from sqlalchemy import (
     Column, String, Integer, ForeignKey, DateTime, Boolean
 )
from sqlalchemy.orm import relationship, declarative base
from sqlalchemy.sql import func

Base = declarative_base()

