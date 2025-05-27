import psycopg2
import bcrypt
import getpass
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
import random
import string

load_dotenv()

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
            elif choice in ["2", "3", "4"]:
                print("\nFeature coming soon!")
            elif choice == "5":
                self.current_user = None
                self.current_user_id = None
                self.is_agent = False
                break
            else:
                print("Invalid option. Please try again.")

    def agency_menu(self):
        """Display agency menu"""
        while True:
            print("\n=== AGENCY ===")
            print("1. Make New Listing")
            print("2. View Existing Listings")
            print("3. Open Chat")
            print("4. Back to Home")
            
            choice = input("Select option: ").strip()
            
            if choice == "4":
                break
            elif choice in ["1", "2", "3"]:
                print("\nFeature coming soon!")
            else:
                print("Invalid option. Please try again.")

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