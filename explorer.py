import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

PROPERTY_TYPES = ['house', 'apartment', 'land', 'commercial']

class Explorer:
    def __init__(self):
        self.conn = self._get_connection()

    def _get_connection(self):
        DB_URL = os.getenv("DATABASE_URL")
        return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

    def _input_filters(self):
        filters = {}
        print("\n--- Set Filters (leave blank to skip) ---")
        price_min = input("Minimum price: ")
        price_max = input("Maximum price: ")
        property_type = input("Property type " + str(PROPERTY_TYPES) + ": ")
        bedrooms = input("Minimum bedrooms: ")
        bathrooms = input("Minimum bathrooms: ")
        if price_min:
            filters['price_min'] = float(price_min)
        if price_max:
            filters['price_max'] = float(price_max)
        if property_type in PROPERTY_TYPES:
            filters['property_type'] = property_type
        if bedrooms:
            filters['bedrooms'] = int(bedrooms)
        if bathrooms:
            filters['bathrooms'] = float(bathrooms)
        return filters

    def _list_properties(self, user_id, filters):
        query = '''
            SELECT listings.id, listings.title, listings.price, listings.property_type, 
                   listings.bedrooms, listings.bathrooms
            FROM listings
            JOIN saved_listings ON listings.id = saved_listings.listing_id
            WHERE saved_listings.user_id = %s
        '''
        params = [user_id]
        if filters.get('price_min'):
            query += " AND listings.price >= %s"
            params.append(filters['price_min'])
        if filters.get('price_max'):
            query += " AND listings.price <= %s"
            params.append(filters['price_max'])
        if filters.get('property_type'):
            query += " AND listings.property_type = %s"
            params.append(filters['property_type'])
        if filters.get('bedrooms'):
            query += " AND listings.bedrooms >= %s"
            params.append(filters['bedrooms'])
        if filters.get('bathrooms'):
            query += " AND listings.bathrooms >= %s"
            params.append(filters['bathrooms'])
        query += " ORDER BY listings.created_at DESC LIMIT 20"

        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def _show_listing_details(self, listing_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM listings WHERE id = %s", (listing_id,))
        listing = cur.fetchone()
        if not listing:
            print("Listing not found.")
            return

        print("\n=== Listing Details ===")
        for key in listing:
            print(f"{key}: {listing[key]}")

        cur.execute("SELECT url, media_type, caption FROM listing_media WHERE listing_id = %s ORDER BY display_order", (listing_id,))
        media = cur.fetchall()
        if media:
            print("\nMedia:")
            for m in media:
                print(f"- {m['media_type']}: {m['url']} ({m['caption']})")
        else:
            print("No media available.")

    def get_properties(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, listing_id, notes, created_at, updated_at
                    FROM saved_listings
                    WHERE user_id = %s
                """, (user_id,))
                results = cur.fetchall()
                if results:
                    print("\n===  Saved Listings ===")
                    for entry in results:
                        print(f"""
 ID: {entry['id']}
 Listing ID: {entry['listing_id']}
 Notes: {entry['notes'] or 'No notes'}
 Created: {entry['created_at']}
 Updated: {entry['updated_at']}
                        """)
                else:
                    print(" No saved listings yet.")
        except psycopg2.Error as e:
            print(" Database Error:", e)

    def menu(self, user_id):
        filters = {}
        while True:
            print("\n=== Explorer ===")
            print("1. List Filtered Properties")
            print("2. Set Filters")
            print("3. View Listing Details")
            print("4. View Saved Listings")
            print("5. Exit")
            choice = input("Select option: ")
            if choice == '1':
                properties = self._list_properties(user_id, filters)
                if not properties:
                    print("No listings found.")
                else:
                    print("\n--- Listings ---")
                    for i, p in enumerate(properties, start=1):
                        print(f"{i}. {p['title']} | Ksh {p['price']} | {p['property_type']} | {p['bedrooms']}bd/{p['bathrooms']}ba")
            elif choice == '2':
                filters = self._input_filters()
            elif choice == '3':
                listing_id = input("Enter listing UUID: ")
                self._show_listing_details(listing_id)
            elif choice == '4':
                self.get_properties(user_id)
            elif choice == '5':
                print(" Goodbye!")
                self.conn.close()
                break
            else:
                print("Invalid option. Try again.")
