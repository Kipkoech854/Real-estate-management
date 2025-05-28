def review_menu(self):
    """Display review management menu"""
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
    """Guide user through creating a review"""
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
        review_id = self.review_system.create_review(
            listing_id, self.current_user_id, rating, comment, media_urls
        )
        if review_id:
            print("\nReview submitted successfully!")
           
            avg, count = self.review_system.calculate_listing_rating(listing_id)
            print(f"\nListing now has {avg}★ average from {count} reviews")
        else:
            print("\nFailed to submit review")

def view_my_reviews(self):
    """Display all reviews by the current user"""
    if not self.current_user_id:
        print("\nPlease login first")
        return
    
    reviews = self.review_system.get_user_reviews(self.current_user_id)
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
    """Display reviews for a specific listing"""
    listing_id = input("Enter listing ID to view reviews: ").strip()
    if not listing_id:
        return
    
    reviews = self.review_system.get_listing_reviews(listing_id)
    if not reviews:
        print("\nNo reviews for this listing yet")
        return
    
    avg, count = self.review_system.calculate_listing_rating(listing_id)
    print(f"\n=== LISTING REVIEWS ({avg}★ from {count} reviews) ===")
    
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