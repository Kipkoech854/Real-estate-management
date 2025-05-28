import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

PROPERTY_TYPES = ['house', 'apartment', 'land', 'commercial']

def get_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def list_properties(conn, filters):
    query = "SELECT id, title, price, property_type, bedrooms, bathrooms FROM listings WHERE status = 'active'"
    params = []
    if 'price_min' in filters and filters['price_min']:
        query = query + " AND price >= %s"
        params.append(filters['price_min'])
    if 'price_max' in filters and filters['price_max']:
        query = query + " AND price <= %s"
        params.append(filters['price_max'])
    if 'property_type' in filters and filters['property_type']:
        query = query + " AND property_type = %s"
        params.append(filters['property_type'])
    if 'bedrooms' in filters and filters['bedrooms']:
        query = query + " AND bedrooms >= %s"
        params.append(filters['bedrooms'])
    if 'bathrooms' in filters and filters['bathrooms']:
        query = query + " AND bathrooms >= %s"
        params.append(filters['bathrooms'])
    query = query + " ORDER BY created_at DESC LIMIT 20"
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchall()


def show_listing_details(conn, listing_id):
    cur = conn.cursor()
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

def input_filters():
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

def explorer_menu():
    conn = get_connection()
    filters = {}
    while True:
        print("")
        print("=== Explorer ===")
        print("1. List Properties")
        print("2. Set Filters")
        print("3. View Listing Details")
        print("4. Exit")
        choice = input("Select option: ")
        if choice == '1':
            properties = list_properties(conn, filters)
            if not properties:
                print("No listings found.")
            else:
                print("")
                print("--- Listings ---")
                i = 1
                for p in properties:
                    print(f"{i}. {p['title']} | Ksh {p['price']} | {p['property_type']} | {p['bedrooms']}bd/{p['bathrooms']}ba")
                    i = i + 1
        elif choice == '2':
            filters = input_filters()
        elif choice == '3':
            listing_id = input("Enter listing UUID: ")
            show_listing_details(conn, listing_id)
        elif choice == '4':
            print("Goodbye!")
            conn.close()
            break
        else:
            print("Invalid option.")

if __name__ == '__main__':
    explorer_menu() 