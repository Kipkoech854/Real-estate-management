import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("DATABASE_URL not found. Make sure it's set in your .env file.")
    sys.exit(1)

try:
    # Connect to the DB
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, price, property_type FROM listings WHERE status = 'active' LIMIT 5;")
    listings = cursor.fetchall()

    print(" Active Listings:")
    for listing in listings:
        print(f"{listing['title']} - Ksh {listing['price']} ({listing['property_type']})")

except Exception as e:
    print(" Failed to connect or query database.")
    print(e)
    sys.exit(1)


FILTERS = {
    'price_min': None,
    'price_max': None,
    'property_type': None,
    'bedrooms': None,
    'bathrooms': None
}

PROPERTY_TYPES = ['house', 'apartment', 'land', 'commercial']


def get_connection():
    if not DB_URL:
        print("DATABASE_URL environment variable not set.")
        sys.exit(1)
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


def list_properties(conn, filters=None):
    query = "SELECT id, title, price, property_type, bedrooms, bathrooms, address FROM listings WHERE status = 'active'"
    params = []
    if filters:
        if filters.get('price_min') is not None:
            query += " AND price >= %s"
            params.append(filters['price_min'])
        if filters.get('price_max') is not None:
            query += " AND price <= %s"
            params.append(filters['price_max'])
        if filters.get('property_type'):
            query += " AND property_type = %s"
            params.append(filters['property_type'])
        if filters.get('bedrooms') is not None:
            query += " AND bedrooms >= %s"
            params.append(filters['bedrooms'])
        if filters.get('bathrooms') is not None:
            query += " AND bathrooms >= %s"
            params.append(filters['bathrooms'])
    query += " ORDER BY created_at DESC LIMIT 20"
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def show_listing_details(conn, listing_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM listings WHERE id = %s", (listing_id,))
        listing = cur.fetchone()
        if not listing:
            print("Listing not found.")
            return
        print("\n=== Listing Details ===")
        for k, v in listing.items():
            print(f"{k}: {v}")
        # Show media
        cur.execute("SELECT url, media_type, caption FROM listing_media WHERE listing_id = %s ORDER BY display_order", (listing_id,))
        media = cur.fetchall()
        if media:
            print("\nMedia:")
            for m in media:
                print(f"- {m['media_type']}: {m['url']} ({m['caption']})")
        else:
            print("No media available.")


def input_filters():
    print("\n--- Set Filters (leave blank to skip) ---")
    try:
        price_min = input("Minimum price: ").strip()
        price_max = input("Maximum price: ").strip()
        property_type = input(f"Property type {PROPERTY_TYPES}: ").strip().lower()
        bedrooms = input("Minimum bedrooms: ").strip()
        bathrooms = input("Minimum bathrooms: ").strip()
        filters = {}
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
    except Exception as e:
        print(f"Invalid input: {e}")
        return {}


def explorer_menu():
    conn = get_connection()
    filters = {}
    while True:
        print("\n=== Explorer ===")
        print("1. List Properties")
        print("2. Set Filters")
        print("3. View Listing Details")
        print("4. Exit")
        choice = input("Select option: ").strip()
        if choice == '1':
            props = list_properties(conn, filters)
            if not props:
                print("No listings found.")
            else:
                print("\n--- Listings ---")
                for i, p in enumerate(props, 1):
                    addr = p['address'].get('city', '') if isinstance(p['address'], dict) else ''
                    print(f"{i}. {p['title']} | ${p['price']} | {p['property_type']} | {p['bedrooms']}bd/{p['bathrooms']}ba | {addr}")
        elif choice == '2':
            filters = input_filters()
        elif choice == '3':
            lid = input("Enter listing UUID: ").strip()
            show_listing_details(conn, lid)
        elif choice == '4':
            print("Goodbye!")
            conn.close()
            break
        else:
            print("Invalid option.")


if __name__ == '__main__':
    explorer_menu() 