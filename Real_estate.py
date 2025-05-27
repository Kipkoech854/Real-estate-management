import os
DB_URL = os.getenv("DATABASE_URL")

if __name__ == '__Real_estate__':
    Real_estate.run()


#property listing
from database import init_db, session
from models import User, Listing

init_db()

agent = User(username="agent_smith", email="smith@agency.com", phone="1234567890", password_hash="hashed_pw", is_agent=True)
session.add(agent)
session.commit()

listing = Listing(
    title="Modern 2BR Apartment",
    description="Spacious apartment in downtown.",
    price=250000.00,
    location="New York, NY",
    property_type="Apartment",
    bedrooms=2,
    bathrooms=2,
    sq_ft=900,
    user_id=agent.id
)
session.add(listing)
session.commit()

print("Listing added successfully!")
