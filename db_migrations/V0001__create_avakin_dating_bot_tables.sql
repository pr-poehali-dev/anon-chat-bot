
CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,
    complaint_count INTEGER DEFAULT 0,
    state TEXT DEFAULT 'idle'
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.profiles (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES t_p59360323_anon_chat_bot.users(id),
    avakin_nick TEXT NOT NULL,
    gender TEXT NOT NULL,
    orientation TEXT NOT NULL,
    age INTEGER NOT NULL,
    photo_file_id TEXT,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.likes (
    id SERIAL PRIMARY KEY,
    from_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    to_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    is_like BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_user_id, to_user_id)
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.chats (
    id SERIAL PRIMARY KEY,
    user_a BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    user_b BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.complaints (
    id SERIAL PRIMARY KEY,
    from_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    to_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.reviews (
    id SERIAL PRIMARY KEY,
    from_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    to_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_user_id, to_user_id)
);

CREATE TABLE IF NOT EXISTS t_p59360323_anon_chat_bot.viewed_profiles (
    user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    viewed_user_id BIGINT REFERENCES t_p59360323_anon_chat_bot.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY(user_id, viewed_user_id)
);

CREATE INDEX IF NOT EXISTS idx_profiles_active ON t_p59360323_anon_chat_bot.profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_chats_active ON t_p59360323_anon_chat_bot.chats(is_active);
CREATE INDEX IF NOT EXISTS idx_likes_from ON t_p59360323_anon_chat_bot.likes(from_user_id);
CREATE INDEX IF NOT EXISTS idx_likes_to ON t_p59360323_anon_chat_bot.likes(to_user_id);
