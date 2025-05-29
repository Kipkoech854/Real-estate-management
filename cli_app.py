import uuid
from Real_estate import ListingManager

def main():
    manager = ListingManager()

    print("\n=== Real Estate CLI ===")
    username = input("Enter your username: ").strip()
    user_id = manager.get_user_id_by_username(username)
    if not user_id:
        print("User not found. Exiting.")
        return

    while True:
        print("\nOptions: [1] Create Listing [2] View My Listings [3] Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            print("\n=== Create Listing ===")
            title = input("Title (required): ").strip()
            if not title:
                print("Title must be filled!")
                continue

            description = input("Description: ").strip() or None
            price = input("Price (optional): ").strip() or None
            if price:
                try:
                    price = float(price)
                except ValueError:
                    print("Invalid price - must be a number")
                    continue

            property_type = input("Property type [house/apartment/land/commercial]: ").strip().lower()
            if property_type not in ['house', 'apartment', 'land', 'commercial']:
                print("Invalid property type")
                continue

            bedrooms = input("Bedrooms: ").strip()
            try:
                bedrooms = int(bedrooms) if bedrooms else None
            except ValueError:
                print("Bedrooms must be a whole number")
                continue

            bathrooms = input("Bathrooms: ").strip()
            try:
                bathrooms = float(bathrooms) if bathrooms else None
            except ValueError:
                print("Bathrooms must be a number")
                continue

            square_feet = input("Square feet: ").strip()
            try:
                square_feet = int(square_feet) if square_feet else None
            except ValueError:
                print("Square feet must be a whole number")
                continue

            address = manager.get_address_input()
            location = manager.get_location_input()

            confirm = input("Create this listing? (y/n): ").lower()
            if confirm == 'y':
                listing_id = manager.create_listing(
                    user_id=user_id,
                    title=title,
                    description=description,
                    price=price,
                    property_type=property_type,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    square_feet=square_feet,
                    address=address,
                    location=location
                )
                if listing_id:
                    print("Listing created successfully!")
                    manager.fetch_user_listings(user_id)
                else:
                    print("Listing creation failed")

        elif choice == '2':
            manager.fetch_user_listings(user_id)

        elif choice == '3':
            print("Goodbye!")
            break

        else:
            print("Invalid option")

    manager.close()

if __name__ == "__main__":
    main()