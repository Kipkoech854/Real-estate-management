import psycopg2
import uuid
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

class ListingManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            sslmode="require"
        )

    def create_user(self, username, email, password_hash, phone=None, is_agent=False):
        try:
            with self.conn.cursor() as cur:
                user_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO users (id, username, email, password_hash, phone, is_agent, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (user_id, username, email, password_hash, phone, is_agent, datetime.utcnow())
                )
                self.conn.commit()
                print(f"User created with ID: {user_id}")
                return user_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"User Creation Error: {e}")
            return None

    def create_listing(self, user_id, title, description, price, property_type,
                       bedrooms, bathrooms, square_feet, address, location):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO listings (
                        id, user_id, title, description, price, property_type, 
                        bedrooms, bathrooms, square_feet, address, location, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeogFromText(%s), %s, %s)
                    RETURNING id;
                    """,
                    (
                        str(uuid.uuid4()), user_id, title, description, price, property_type,
                        bedrooms, bathrooms, square_feet, json.dumps(address),
                        f"POINT({location['lng']} {location['lat']})",
                        datetime.utcnow(), datetime.utcnow()
                    )
                )
                listing_id = cur.fetchone()[0]
                self.conn.commit()
                print(f"\nListing created with ID: {listing_id}")
                return listing_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"\nDatabase Error: {e}")
            return None

    def get_all_listings(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, title, price, property_type, status FROM listings WHERE status = 'active'")
                listings = cur.fetchall()
                print("\n=== Active Listings ===")
                for l in listings:
                    print(f"ID: {l[0]} | Title: {l[1]} | Price: ${l[2]} | Type: {l[3]} | Status: {l[4]}")
                return listings
        except psycopg2.Error as e:
            print(f"\nDatabase Error: {e}")
            return []

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    manager = ListingManager()

    user_id = manager.create_user(
        username="exampleuser",
        email="example@example.com",
        password_hash="hashed_password_here",
        phone="555-1234",
        is_agent=False
    )

    if user_id:
        manager.create_listing(
            user_id=user_id,
            title="Modern Downtown Apartment",
            description="2 bed, 1.5 bath near Embarcadero with great amenities.",
            price=4500.00,
            property_type="apartment",
            bedrooms=2,
            bathrooms=1.5,
            square_feet=950,
            address={
                "street": "123 Market St",
                "city": "Nairobi",
                "county": "Nairobi"
            },
            location={"lat": 37.7955, "lng": -122.3937}
        )

        manager.get_all_listings()

    manager.close()
