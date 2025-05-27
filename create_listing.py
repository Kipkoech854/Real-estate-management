from database import init_db, session
from models import User, PropertyListing

init_db()

agent = User(
    username="agent_john",
    email="john@agency.com",
    phone="555-6789",
    password_hash="secure_hash",
    is_agent=True
)
session.add(agent)
session.commit()

print(f"Agent created with ID: {agent.id}")

listing = PropertyListing(
    title="Spacious 3BR Apartment",
    description="Modern apartment in a great location.",
    price=320000.00,
    location="Nairobi, Kenya",
    property_type="Apartment",
    bedrooms=3,
    bathrooms=2,
    sq_ft=1200,
    user_id=agent.id
)
session.add(listing)
session.commit()

print(" Listing added successfully!")
