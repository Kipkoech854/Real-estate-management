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
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD") or os.getenv("DB_PASS"),  # Handles both versions
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            sslmode="require" if os.getenv("DB_SSL") == "true" else None
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

    def get_user_id_by_username(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Error fetching user: {e}")
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

    def fetch_user_listings(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, price, property_type, status
                    FROM listings
                    WHERE user_id = %s
                """, (user_id,))
                listings = cur.fetchall()
                print("\n=== Your Listings ===")
                for l in listings:
                    print(f"ID: {l[0]} | Title: {l[1]} | Price: ${l[2]} | Type: {l[3]} | Status: {l[4]}")
                return listings
        except psycopg2.Error as e:
            print(f"Error fetching user's listings: {e}")
            return []

    def get_address_input(self):
        print("\nEnter Address Info:")
        return {
            "street": input("Street: ").strip(),
            "city": input("City: ").strip(),
            "state": input("State: ").strip(),
            "zip": input("ZIP: ").strip(),
        }

    def get_location_input(self):
        print("\nEnter Coordinates:")
        lat = input("Latitude: ").strip()
        lng = input("Longitude: ").strip()
        try:
            return {"lat": float(lat), "lng": float(lng)}
        except ValueError:
            print("Invalid coordinates. Setting to 0, 0.")
            return {"lat": 0.0, "lng": 0.0}

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    manager = ListingManager()

   