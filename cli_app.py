import psycopg2
import bcrypt
import getpass
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
import random
import string
import json





class RealEstateCLI:
    def __init__(self):
        """Initialize database connection"""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            sslmode="require"
        )
        self.current_user = None
        self.current_user_id = None
        self.is_agent = False

    def _hash_password(self, password):
        """Securely hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _check_username_exists(self, username):
        """Check if username already exists in database"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            return cur.fetchone() is not None

    def _check_agency_exists(self, name):
        """Check if agency name already exists"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM agencies WHERE name = %s", (name,))
            return cur.fetchone() is not None

    def _verify_credentials(self, username, password):
        """Verify username and password against database"""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash, is_agent FROM users WHERE username = %s", 
                (username,)
            )
            result = cur.fetchone()
            if result:
                user_id, stored_hash, is_agent = result
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    return user_id, is_agent
        return None, False

    def _generate_license_number(self, state_code="CA"):
        """Generate unique license number"""
        current_year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{state_code}RE-{current_year}-{random_part}"

    def create_account(self):
        """Handle new user registration"""
        print("\n=== Create New Account ===")
        
        while True:
            username = input("Username: ").strip()
            if not self._check_username_exists(username):
                break
            print("\nUsername already taken. Please try another.")
        
        email = input("Email (optional): ").strip() or None
        phone = input("Phone (optional): ").strip() or None
        
        while True:
            password = getpass.getpass("Password: ")
            confirm = getpass.getpass("Confirm Password: ")
            if password == confirm:
                break
            print("\nError: Passwords don't match!")
        
        is_agent = input("Are you registering as an agent? (y/n): ").lower() == 'y'
        
        try:
            user_id = str(uuid.uuid4())
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (
                        id, username, email, phone, 
                        password_hash, is_agent, last_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        user_id, username, email, phone,
                        self._hash_password(password), is_agent, datetime.utcnow()
                    )
                )
                self.conn.commit()
                print("\nAccount created successfully!")
                self.current_user = username
                self.current_user_id = user_id
                self.is_agent = is_agent
                return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"\nDatabase Error: {e}")
            return False

    def login(self):
        """Handle user login"""
        print("\n=== Login to Your Account ===")
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        user_id, is_agent = self._verify_credentials(username, password)
        if user_id:
            print(f"\nWelcome back, {username}!")
            self.current_user = username
            self.current_user_id = user_id
            self.is_agent = is_agent
            return True
        else:
            print("\nInvalid username or password")
            return False

    def register_agency(self):
        """Register a new agency"""
        if not self.current_user_id:
            print("\nPlease login first")
            return
        
        print("\n=== Register New Agency ===")
        
        while True:
            name = input("Agency Name: ").strip()
            if not self._check_agency_exists(name):
                break
            print("\nAn agency with this name already exists. Please try another.")
        
        bio = input("Bio : ").strip() 
        profile_image_url = input("Profile Image *URL : ").strip() 
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO agencies (
                        id, user_id, name, license_number, 
                        bio, profile_image_url
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        str(uuid.uuid4()), self.current_user_id, name,
                        self._generate_license_number(), bio, profile_image_url
                    )
                )
                self.conn.commit()
                print("\nAgency registered successfully!")
                return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"\nDatabase Error: {e}")
            return False

    def has_agency(self):
        """Check if user has an agency"""
        if not self.current_user_id:
            return False
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM agencies WHERE user_id = %s", 
                (self.current_user_id,)
            )
            return cur.fetchone() is not None

    def home_menu(self):
        """Display home menu after login/registration"""
        while True:
            print("\n=== HOME ===")
            print("1. Register Agency" if not self.has_agency() else "1. Go to Agency")
            print("2. See Listings")
            print("3. Open Ratings")
            print("4. Open Explorer")
            print("5. Logout")
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                if self.has_agency():
                    self.agency_menu()
                else:
                    self.register_agency()
            elif choice == "2":
                self.get_all_listings()
                self.save_listings_to_Explorer()

            elif choice in ["3", "4"]:
                print("\nFeature coming soon!")
            elif choice == "5":
                self.current_user = None
                self.current_user_id = None
                self.is_agent = False
                break
            else:
                print("Invalid option. Please try again.")


    def create_listing(self, user_id , title, description, price, property_type, bedrooms, bathrooms, square_feet, address, location):
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
                        location,
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
    
    def save_listings_to_Explorer(self):
        title = input("Enter title of listing to save it for further exploration: ").strip() or None
        if not title:
            print("Listing title is required.")
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM listings WHERE title = %s", (title,))
                result = cur.fetchone()
                if not result:
                    print("Listing not found.")
                    return

                listing_id = result[0]
                
                notes = input("Add any notes (optional): ").strip() or None
                
                cur.execute(
                """
                INSERT INTO saved_listings (id, user_id, listing_id, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (user_id, listing_id) DO UPDATE 
                SET notes = EXCLUDED.notes, updated_at = NOW()
                """,
                (str(uuid.uuid4()), self.current_user_id, listing_id, notes)
                )

                self.conn.commit()
                print("Listing saved for future exploration.")

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Database error: {e}")

            
    def agency_menu(self):
        """Display agency menu"""
        while True:
            print("\n=== AGENCY ===")
            print("1. Make New Listing")
            print("2. View Existing Listings")
            print("3. Open Chat")
            print("4. Open reviews")
            print("5. View Agency details")
            print("6. Back to Home")

            choice = input("Select option: ").strip()
        
            if choice == "6":
                break
            elif choice == "1":
                print("\n=== create listing ===")
                title = input("Title (required): ").strip()
                if not title:
                    print('Title must be filled!')
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
                
                address = self.get_address_input() 
                location = self.get_location_input() 
            
                confirm = input("Create this listing? (y/n): ").lower()
                if confirm == 'y':
                    listing_id = self.create_listing(
                    user_id=self.current_user_id,  
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
                else:
                    print("Listing creation cancelled")

            elif choice == "2":
                print("\nFeature coming soon!")
            elif choice == "3":
                try:
                    from chatsystem import ChatSystem  
                    chat_app = ChatSystem(self.conn, self.current_user_id)
                    chat_app.cli_interface()  
                except Exception as e:
                    print(f"Failed to launch chat system: {e}")
            elif choice == "4":
                try:
                    from feedbck_system import FeedbackSystem
                    feedback_cli = FeedbackSystem(self.current_user_id)
                    feedback_cli.review_menu()
                except Exception as e:
                    print(f"Failed to launch feedback system: {e}")
            elif choice == "5":
                self.display_agency_details()
            else:
                print("Invalid option. Please try again.")


    def display_agency_details(self):
        print("\n=== My Agency ===")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                """
                SELECT name, license_number, bio, verified, profile_image_url, created_at
                FROM agencies
                WHERE user_id = %s
                """,
                (self.current_user_id,)
                )
                result = cur.fetchone()

                if result:
                    fields = ["Name", "License Number", "Bio", "Verified", "Profile Image", "Created At"]
                    for field, value in zip(fields, result):
                        print(f"{field}: {value}")
                else:
                    print("No agency details found.")
    
        except psycopg2.Error as e:
            print(f"Database error: {e}")



    def get_location_input(self):
        """Helper method to get location coordinates"""
        while True:
            coords = input("Enter coordinates as 'latitude,longitude' (optional): ").strip()
            if not coords:
                return None
        try:
            lat, lng = map(float, coords.split(','))
            return {'lat': lat, 'lng': lng}
        except ValueError:
            print("Invalid format. Please enter like: -1.286389,36.817223")

    def get_address_input(self):
        print("Please enter the property address:")
        street = input("Street: ").strip()
        city = input("City: ").strip()
        county = input("County: ").strip()
    
        address = {
            "street": street if street else None,
            "city": city if city else None,
            "county": county if county else None
    }
    
        return address        



    def run(self):
        """Main application loop"""
        while True:
            print("\n=== MAIN MENU ===")
            print("1. Create New Account")
            print("2. Login")
            print("3. Exit")
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                if self.create_account():
                    self.home_menu()
            elif choice == "2":
                if self.login():
                    self.home_menu()
            elif choice == "3":
                break
            else:
                print("Invalid option. Please try again.")
        
        self.conn.close()
        print("\nGoodbye!")
    











if __name__ == "__main__":
    app = RealEstateCLI()
    app.run()