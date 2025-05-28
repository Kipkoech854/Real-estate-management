import psycopg2
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

class FeedbackSystem:
    def __init__(self):
        self.current_user_id = None
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            sslmode="require"
        )
        
    def review_menu(self):
        while True:
            print("\n=== REVIEW MANAGEMENT ===")
            print("1. Leave a review for a listing")
            print("2. View my reviews")
            print("3. View listing reviews")
            print("4. Back to main menu")
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                self.create_review_flow()
            elif choice == "2":
                self.view_my_reviews()
            elif choice == "3":
                self.view_listing_reviews()
            elif choice == "4":
                break
            else:
                print("Invalid option. Please try again.")

    def create_review_flow(self):
        if not self.current_user_id:
            print("\nPlease login first")
            return

        saved_listings = self.get_saved_listings(self.current_user_id)
        if not saved_listings:
            print("\nYou haven't saved any listings to review")
            return
        
        print("\nYour saved listings:")
        for i, listing in enumerate(saved_listings, 1):
            print(f"{i}. {listing[1]} (ID: {listing[0]})")
        
        try:
            selection = int(input("Select listing to review (0 to cancel): "))
            if selection == 0:
                return
            listing_id = saved_listings[selection-1][0]
        except (ValueError, IndexError):
            print("Invalid selection")
            return
        
        if self.has_reviewed_listing(self.current_user_id, listing_id):
            print("\nYou've already reviewed this listing")
            return
        
        while True:
            try:
                rating = int(input("Rating (1-5 stars): "))
                if 1 <= rating <= 5:
                    break
                print("Rating must be between 1 and 5")
            except ValueError:
                print("Please enter a number")
        
        comment = input("Comment (optional, press enter to skip): ").strip() or None

        media_urls = []
        while True:
            url = input("Add media URL (or press enter to finish): ").strip()
            if not url:
                break
            media_urls.append(url)

        print("\nReview summary:")
        print(f"Rating: {'★' * rating}{'☆' * (5 - rating)}")
        if comment:
            print(f"Comment: {comment}")
        if media_urls:
            print(f"Media: {len(media_urls)} items")

        confirm = input("\nSubmit this review? (y/n): ").lower()
        if confirm == 'y':
            review_id = self.post_review(listing_id, rating, comment, media_urls)
            if review_id:
                print("\nReview submitted successfully!")
                avg, count = self.calculate_listing_rating(listing_id)
                print(f"\nListing now has {avg:.1f}★ average from {count} reviews")
            else:
                print("\nFailed to submit review")

    def post_review(self, listing_id, rating, comment, media_urls=None):
        if not self.current_user_id:
            print("\nPlease login first")
            return False

        try:
            with self.conn.cursor() as cur:
                review_id = str(uuid.uuid4())
                now = datetime.now()
                cur.execute(
                    """
                    INSERT INTO reviews (
                        id, listing_id, reviewer_id, rating, comment, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        review_id,
                        listing_id,
                        self.current_user_id,
                        rating,
                        comment,
                        now,
                        now
                    )
                )

                if media_urls:
                    for idx, url in enumerate(media_urls):
                        media_id = str(uuid.uuid4())
                        cur.execute(
                            """
                            INSERT INTO listing_media (
                                id, listing_id, url, media_type, caption, display_order, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                media_id,
                                listing_id,
                                url,
                                'image',
                                None,
                                idx + 1,
                                now
                            )
                        )

                self.conn.commit()
                return review_id

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"\nDatabase Error: {e}")
            return False

    def view_my_reviews(self):
        if not self.current_user_id:
            print("\nPlease login first")
            return

        reviews = self.get_user_reviews(self.current_user_id)
        if not reviews:
            print("\nYou haven't written any reviews yet")
            return

        print("\n=== YOUR REVIEWS ===")
        for review in reviews:
            id, title, rating, comment, created_at, media_urls = review
            print(f"\nListing: {title}")
            print(f"Date: {created_at.strftime('%Y-%m-%d')}")
            print(f"Rating: {'★' * rating}{'☆' * (5 - rating)}")
            if comment:
                print(f"Comment: {comment}")
            if media_urls and media_urls[0]:
                print(f"Media: {len([m for m in media_urls if m])} items")
            print("-" * 40)

    def view_listing_reviews(self):
        listing_id = input("Enter listing ID to view reviews: ").strip()
        if not listing_id:
            return

        reviews = self.get_listing_reviews(listing_id)
        if not reviews:
            print("\nNo reviews for this listing yet")
            return

        avg, count = self.calculate_listing_rating(listing_id)
        print(f"\n=== LISTING REVIEWS ({avg:.1f}★ from {count} reviews) ===")

        for review in reviews:
            id, username, rating, comment, created_at, media_urls = review
            print(f"\nReview by: {username}")
            print(f"Date: {created_at.strftime('%Y-%m-%d')}")
            print(f"Rating: {'★' * rating}{'☆' * (5 - rating)}")
            if comment:
                print(f"Comment: {comment}")
            if media_urls and media_urls[0]:
                print(f"Media: {len([m for m in media_urls if m])} items")
            print("-" * 40)

    def get_saved_listings(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT l.id, l.title 
                    FROM listings l
                    JOIN saved_listings sl ON l.id = sl.listing_id
                    WHERE sl.user_id = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM reviews r 
                        WHERE r.listing_id = l.id AND r.reviewer_id = %s
                    )
                    """,
                    (user_id, user_id)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []

    def has_reviewed_listing(self, user_id, listing_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM reviews WHERE reviewer_id = %s AND listing_id = %s",
                    (user_id, listing_id)
                )
                return cur.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return False

    def get_user_reviews(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.id, l.title, r.rating, r.comment, r.created_at, 
                           ARRAY_AGG(lm.url) AS media_urls
                    FROM reviews r
                    JOIN listings l ON r.listing_id = l.id
                    LEFT JOIN listing_media lm ON lm.listing_id = l.id AND lm.id IN (
                        SELECT id FROM listing_media 
                        WHERE listing_id = l.id 
                        ORDER BY display_order 
                        LIMIT 3
                    )
                    WHERE r.reviewer_id = %s
                    GROUP BY r.id, l.title
                    ORDER BY r.created_at DESC
                    """,
                    (user_id,)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []

    def get_listing_reviews(self, listing_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.id, u.username, r.rating, r.comment, r.created_at, 
                           ARRAY_AGG(lm.url) AS media_urls
                    FROM reviews r
                    JOIN users u ON r.reviewer_id = u.id
                    LEFT JOIN listing_media lm ON lm.listing_id = r.listing_id AND lm.id IN (
                        SELECT id FROM listing_media 
                        WHERE listing_id = r.listing_id 
                        ORDER BY display_order 
                        LIMIT 3
                    )
                    WHERE r.listing_id = %s
                    GROUP BY r.id, u.username
                    ORDER BY r.created_at DESC
                    """,
                    (listing_id,)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []

    def calculate_listing_rating(self, listing_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT AVG(rating)::numeric(10,1), COUNT(*)
                    FROM reviews
                    WHERE listing_id = %s
                    """,
                    (listing_id,)
                )
                result = cur.fetchone()
                return result if result else (0, 0)
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return (0, 0)

    def run(self):
       
        self.current_user_id = "test_user_id"  
        self.review_menu()


if __name__ == "__main__":
    app = FeedbackSystem()
    app.run()