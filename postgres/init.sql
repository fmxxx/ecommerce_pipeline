CREATE TABLE IF NOT EXISTS user_authentication (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS user_public_profile (
    user_id UUID PRIMARY KEY REFERENCES user_authentication(id) ON DELETE CASCADE,
    display_name VARCHAR(50) NOT NULL,
    photo_url VARCHAR(255),
    member_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS user_private_profile (
    user_id UUID PRIMARY KEY REFERENCES user_authentication(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    phone VARCHAR(20),
    birth_date DATE,
    gender VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS products (
    uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    cost_price DECIMAL(10, 2),
    sale_price DECIMAL(10, 2) NOT NULL,
    text_description VARCHAR,
    specifications JSONB
);

CREATE TABLE IF NOT EXISTS orders (
    uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_authentication(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(uuid) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_authentication(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(uuid) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    publication_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);