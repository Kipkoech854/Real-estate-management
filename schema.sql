-- Load extensions first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";
DROP TABLE IF EXISTS reviews;

DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS saved_listings;
DROP TABLE IF EXISTS listing_media;
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS agencies;
DROP TABLE IF EXISTS users;

-- Core tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_agent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ
);

CREATE TABLE agencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) UNIQUE,
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    profile_image_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(12,2),
    property_type VARCHAR(50) CHECK (property_type IN ('house', 'apartment', 'land', 'commercial')),
    bedrooms INT,
    bathrooms DECIMAL(3,1),
    square_feet INT,
    address JSONB NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'pending', 'sold', 'rented')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media table
CREATE TABLE listing_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    url VARCHAR(255) NOT NULL,
    media_type VARCHAR(20) CHECK (media_type IN ('image', 'video', 'virtual_tour', 'floor_plan')),
    caption VARCHAR(200),
    display_order INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saved listings
CREATE TABLE saved_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, listing_id)
);

-- Conversations system
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_1 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_2 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (participant_1, participant_2)
);

-- Chats table
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    attachments JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saved listing chats (different from conversation chats)


-- Add the active_chat_id column after saved_listing_chats exists
ALTER TABLE saved_listings 
ADD COLUMN active_chat_id UUID REFERENCES saved_listing_chats(id) ON DELETE SET NULL;

-- Reviews
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_property_type ON listings(property_type);

CREATE INDEX idx_listings_location ON listings USING GIST(location);

-- Remove this index as the table doesn't exist
-- CREATE INDEX idx_agency_chats_user ON agency_chats(user_id);