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
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

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

    def fetch_user_listings(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                SELECT id, title, price, property_type, status
                FROM listings
                WHERE user_id = %s
                """, (user_id,))
                listings = cur.fetchall()

                if listings:
                    print("\n=== 📋 Your Listings ===")
                    for l in listings:
                        print("\n" + "-" * 50)
                        print(f"🆔 ID       : {l[0]}")
                        print(f"🏷️  Title    : {l[1]}")
                        print(f"💰 Price    : ${l[2]:,.2f}")
                        print(f"🏘️  Type     : {l[3]}")
                        print(f"📦 Status   : {l[4]}")
                        print("-" * 50)
                else:
                    print("\n⚠️  No listings found for this user.")
        except psycopg2.Error as e:
            print(f"❌ Error fetching user's listings: {e}")

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
