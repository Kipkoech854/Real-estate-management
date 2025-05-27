from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    is_agent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listings = relationship("PropertyListing", back_populates="user")

    agency_id = Column(String, ForeignKey('agencies.id'))
    agency = relationship("Agency", back_populates="users")


class Agency(Base):
    __tablename__ = 'agencies'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    license_no = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="agency")

class PropertyListing(Base):
    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    location = Column(String)
    property_type = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    sq_ft = Column(Float)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="listings")
    media = relationship("Media", back_populates="listing")

class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    type = Column(String)
    listing_id = Column(Integer, ForeignKey('listings.id'))

    listing = relationship("PropertyListing", back_populates="media")