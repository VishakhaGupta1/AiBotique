-- Real Fashion Recommendation Database Schema

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table (Real Products)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    color VARCHAR(50),
    size VARCHAR(10),
    price DECIMAL(10,2),
    image_url TEXT,
    description TEXT,
    target_gender VARCHAR(10),
    target_age_min INTEGER,
    target_age_max INTEGER,
    season VARCHAR(20),
    material VARCHAR(100),
    in_stock BOOLEAN DEFAULT TRUE,
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Outfits Table (Pre-curated Combinations)
CREATE TABLE outfits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    style_category VARCHAR(50),
    color_scheme VARCHAR(50),
    total_price DECIMAL(10,2),
    target_gender VARCHAR(10),
    target_age_min INTEGER,
    target_age_max INTEGER,
    occasion VARCHAR(50),
    season VARCHAR(20),
    difficulty_level VARCHAR(20), -- easy, medium, expert
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Outfit Items (Link Table)
CREATE TABLE outfit_items (
    id SERIAL PRIMARY KEY,
    outfit_id INTEGER REFERENCES outfits(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    item_type VARCHAR(20), -- top, bottom, shoes, accessory
    position_order INTEGER, -- for layering
    is_optional BOOLEAN DEFAULT FALSE
);

-- User Preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    preferred_colors TEXT[], -- array of colors
    preferred_styles TEXT[], -- array of styles
    preferred_brands TEXT[],
    budget_range_min DECIMAL(10,2),
    budget_range_max DECIMAL(10,2),
    size VARCHAR(10),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Interactions (For ML Training)
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    outfit_id INTEGER REFERENCES outfits(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20), -- view, like, purchase, share
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations Log
CREATE TABLE recommendation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    outfit_id INTEGER REFERENCES outfits(id) ON DELETE CASCADE,
    algorithm_used VARCHAR(50),
    score DECIMAL(5,2),
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample Real Products Data
INSERT INTO products (name, brand, category, subcategory, color, size, price, image_url, description, target_gender, target_age_min, target_age_max, season, material, in_stock) VALUES
-- Men's Products
('Classic White Oxford Shirt', 'Van Heusen', 'formal', 'shirts', 'white', 'M', 1899.00, 'https://images.unsplash.com/photo-1596755094514-f87e40cc0606?w=300&h=300&fit=crop', 'Premium cotton oxford shirt perfect for office wear', 'male', 22, 45, 'all', 'cotton', true),
('Navy Blue Blazer', 'Park Avenue', 'formal', 'jackets', 'navy', 'L', 3499.00, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop', 'Professional navy blazer for business meetings', 'male', 25, 50, 'all', 'wool blend', true),
('Black Denim Jeans', 'Levis', 'casual', 'jeans', 'black', '32', 2499.00, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop', 'Classic fit black denim jeans', 'male', 18, 35, 'all', 'denim', true),
('White Sneakers', 'Nike', 'casual', 'shoes', 'white', '9', 4499.00, 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop', 'Comfortable white sneakers for everyday wear', 'male', 16, 40, 'all', 'synthetic', true),
('Gray Hoodie', 'Puma', 'casual', 'hoodies', 'gray', 'L', 2999.00, 'https://images.unsplash.com/photo-1556851295518-3b29f0e2b876?w=300&h=300&fit=crop', 'Comfortable gray hoodie for casual outings', 'male', 18, 30, 'winter', 'cotton blend', true),

-- Women's Products  
('Black Evening Dress', 'Zara', 'formal', 'dresses', 'black', 'M', 5799.00, 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=300&h=300&fit=crop', 'Elegant black evening dress for special occasions', 'female', 20, 40, 'all', 'polyester', true),
('Blue Denim Jacket', 'Mango', 'casual', 'jackets', 'blue', 'S', 3499.00, 'https://images.unsplash.com/photo-1574323387217-5d5c9e0c0746?w=300&h=300&fit=crop', 'Stylish blue denim jacket', 'female', 18, 35, 'spring', 'denim', true),
('White Blouse', 'H&M', 'formal', 'tops', 'white', 'M', 1899.00, 'https://images.unsplash.com/photo-1483985988355-763628e1915e?w=300&h=300&fit=crop', 'Crisp white blouse for office wear', 'female', 22, 45, 'all', 'cotton', true),
('Black Heels', 'Aldo', 'formal', 'shoes', 'black', '7', 3299.00, 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop', 'Elegant black heels for formal occasions', 'female', 18, 45, 'all', 'synthetic', true),
('Beige Flats', 'Bata', 'casual', 'shoes', 'beige', '6', 1999.00, 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop', 'Comfortable beige flats for daily wear', 'female', 16, 50, 'all', 'leather', true),

-- Unisex Products
('Black Leather Belt', 'Woodland', 'accessories', 'belts', 'black', 'M', 1499.00, 'https://images.unsplash.com/photo-1544967348-c7ceb6ec5ec0?w=300&h=300&fit=crop', 'Genuine leather belt', 'unisex', 18, 50, 'all', 'leather', true),
('Silver Watch', 'Titan', 'accessories', 'watches', 'silver', 'M', 2599.00, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop', 'Elegant silver watch', 'unisex', 20, 45, 'all', 'stainless steel', true),
('Brown Sunglasses', 'Ray-Ban', 'accessories', 'sunglasses', 'brown', 'M', 2499.00, 'https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=300&h=300&fit=crop', 'Stylish brown sunglasses', 'unisex', 16, 40, 'summer', 'plastic', true);

-- Sample Outfits
INSERT INTO outfits (name, description, style_category, color_scheme, total_price, target_gender, target_age_min, target_age_max, occasion, season, difficulty_level) VALUES
('Business Professional', 'Complete business outfit for office meetings', 'formal', 'navy_white', 12497.00, 'male', 25, 45, 'work', 'all', 'easy'),
('Casual Streetwear', 'Trendy streetwear outfit for weekends', 'casual', 'blue_black', 8497.00, 'male', 18, 30, 'casual', 'all', 'easy'),
('Elegant Evening', 'Sophisticated evening outfit for special occasions', 'formal', 'black', 15497.00, 'female', 25, 40, 'formal', 'all', 'medium'),
('Summer Casual', 'Light and comfortable summer outfit', 'casual', 'yellow_beige', 6797.00, 'female', 18, 30, 'casual', 'summer', 'easy'),
('Weekend Comfort', 'Relaxed outfit for weekend outings', 'casual', 'blue_white', 7497.00, 'unisex', 18, 35, 'casual', 'all', 'easy');

-- Link Outfits with Products
INSERT INTO outfit_items (outfit_id, product_id, item_type, position_order) VALUES
-- Business Professional Outfit (outfit_id = 1)
(1, 1, 'top', 1),        -- White Oxford Shirt
(1, 2, 'top', 2),        -- Navy Blazer  
(1, 3, 'bottom', 1),     -- Black Denim Jeans
(1, 4, 'shoes', 1),       -- White Sneakers
(1, 11, 'accessory', 1),  -- Leather Belt
(1, 12, 'accessory', 2),  -- Silver Watch

-- Casual Streetwear Outfit (outfit_id = 2)
(2, 5, 'top', 1),         -- Gray Hoodie
(2, 3, 'bottom', 1),      -- Black Denim Jeans  
(2, 4, 'shoes', 1),       -- White Sneakers

-- Elegant Evening Outfit (outfit_id = 3)
(3, 6, 'top', 1),         -- Black Evening Dress
(3, 9, 'shoes', 1),       -- Black Heels
(3, 11, 'accessory', 1),  -- Leather Belt
(3, 12, 'accessory', 2),  -- Silver Watch

-- Summer Casual Outfit (outfit_id = 4)
(4, 7, 'top', 1),         -- Blue Denim Jacket
(4, 8, 'top', 2),         -- White Blouse
(4, 10, 'shoes', 1),      -- Beige Flats
(4, 13, 'accessory', 1),  -- Sunglasses

-- Weekend Comfort Outfit (outfit_id = 5)
(5, 7, 'top', 1),         -- Blue Denim Jacket
(5, 1, 'top', 2),         -- White Oxford Shirt
(5, 3, 'bottom', 1),      -- Black Denim Jeans
(5, 4, 'shoes', 1);       -- White Sneakers
