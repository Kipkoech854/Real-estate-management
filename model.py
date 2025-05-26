+----------------+       +----------------+       +-------------------+
|     User       |       |    Agency      |       |     Listing       |
+----------------+       +----------------+       +-------------------+
| - id (PK)      |<>-----| - id (PK)      |<>-----| - id (PK)         |
| - username     |       | - name         |       | - title           |
| - email        |       | - license_no   |       | - description     |
| - phone        |       | - bio          |       | - price           |
| - password_hash|       | - verified     |       | - location        |
| - is_agent     |       | - user_id (FK) |       | - property_type   |
| - created_at   |       +----------------+       | - bedrooms        |
+----------------+            ^                   | - bathrooms       |
       |                      |                   | - sq_ft           |
       |                +----------------+       | - created_at      |
       |                |    AgencyChat  |       | - user_id (FK)    |
       |                +----------------+       +-------------------+
+----------------+       | - id (PK)      |             ^
|   SavedListing |       | - agency_id(FK)|     +-------------------+
+----------------+       | - user_id (FK) |     |    Media          |
| - id (PK)      |       | - message      |     +-------------------+
| - user_id (FK) |       | - timestamp    |     | - id (PK)         |
| - listing_id   |       | - attachments  |     | - url             |
| - saved_at     |       +----------------+     | - type            |
| - notes        |                              | - listing_id (FK) |
| - chat_thread<>|------------------------------+-------------------+
+----------------+       +----------------+             ^
       ^                |    Review      |             |
       |                +----------------+             |
       |                | - id (PK)      |     +-------------------+
       +----------------| - rating       |     | SavedListingChat  |
                        | - comment      |     +-------------------+
                        | - images[]     |     | - id (PK)         |
                        | - created_at   |     | - saved_listing_id|
                        | - user_id (FK) |     | - user_id (FK)    |
                        | - listing_id   |     | - message         |
                        +----------------+     | - timestamp       |
                                               +-------------------+




1. User
Core entity for all platform participants

Fields:

id (PK): Unique identifier (UUID recommended)

username: Unique display name

email & phone: Login credentials (at least one required)

password_hash: Securely hashed password

is_agent: Boolean flag for agent status

created_at: Timestamp

2. Agency
Extended profile for agent users

Fields:

id (PK): Unique identifier

name: Legal business name

license_no: Government-issued license

bio: Description of services

verified: Admin-approved status

user_id (FK): Linked to User (one-to-one)

3. Listing
Property advertisement

Fields:

id (PK): Unique identifier

title: Short property name

description: Detailed features

price: Decimal value

location: Geo-coordinates/address

property_type: House/Apartment/etc.

bedrooms, bathrooms, sq_ft: Metrics

user_id (FK): Listing owner (agent or regular user)

4. Media
Visual content for listings

Fields:

id (PK): Unique identifier

url: Cloud storage path

type: image/video/3d_tour

listing_id (FK): Parent listing

5. SavedListing
User's favorite properties

Fields:

id (PK): Unique identifier

user_id (FK): Saver's account

listing_id (FK): Saved property

saved_at: Timestamp

notes: Private user comments

chat_thread_id (FK): Linked to SavedListingChat

6. Review
Feedback on listings

Fields:

id (PK): Unique identifier

rating (1-5): Star rating

comment: Text feedback

images[]: Array of image URLs

user_id (FK): Reviewer

listing_id (FK): Reviewed property

7. AgencyChat
Communication channel with agencies

Fields:

id (PK): Unique identifier

agency_id (FK): Target agency

user_id (FK): Client user

message: Text content

timestamp: Auto-generated

attachments: JSON array of file URLs

8. SavedListingChat
Property-specific discussions

Fields:

id (PK): Unique identifier

saved_listing_id (FK): Linked saved listing

user_id (FK): Participant

message: Text content

timestamp: Auto-generated

Key Relationships
User → Agency: One-to-one (User becomes agent)

User → Listing: One-to-many (User owns listings)

Listing → Media: One-to-many

User → SavedListing: One-to-many (Favorites system)

SavedListing → SavedListingChat: One-to-many (Threaded chats)

Agency → AgencyChat: One-to-many (Support inbox)



Chat Workflows:

Auto-create SavedListingChat when property is saved

Notify agents on new AgencyChat messages

Explorer Feature:

SavedListing acts as persistent user collection

Chats attached to saved items retain context

Security Notes
Auth Required for all chat operations

Ownership Checks:

Only listing owners can modify media

Users can only access their own SavedListingChats

Data Retention:



Example API Flow
User saves listing:

Creates SavedListing record

Auto-generates SavedListingChat thread

Messages agent:

Posts to /agency/chats → Creates AgencyChat record

Leaves review:

Posts to /listings/{id}/reviews → Creates Review record

CLI MODEL

start
enter Email,phone
 enter Password

1.display listings
2.create agency but if agent view agency :1.create new listing
                                          2.open chats.
                                          3 view listing reviews.
3.rate listing: 1. Stars either 1-5
                2. Text
                3.media
4 open Explorer and chats : 1.view explored listings
                             2.open chats. :display names of users you have chats with -> type name to show chats with the person with option to send new chat
