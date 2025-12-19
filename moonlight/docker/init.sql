-- Moonlight Database Initialization
-- PostgreSQL + pgvector

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    preferences JSONB DEFAULT '{}',
    voice_profile JSONB DEFAULT '{}'
);

-- Conversations table (Mid-term memory)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    session_id VARCHAR(255),
    
    -- Message content
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    
    -- Vector embeddings (768 dimensions for all-MiniLM-L6-v2)
    user_embedding vector(384),
    assistant_embedding vector(384),
    
    -- Metadata
    emotional_tone VARCHAR(50),
    importance_score FLOAT,
    tools_used JSONB,
    principles_applied JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- User profiles table (Long-term memory)
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) UNIQUE,
    
    -- Preferences & patterns
    preferences JSONB DEFAULT '{}',
    patterns JSONB DEFAULT '{}',
    emotional_baseline JSONB DEFAULT '{}',
    critical_moments JSONB DEFAULT '[]',
    
    -- Relationship data
    relationship_depth INT DEFAULT 1,
    days_together INT DEFAULT 0,
    total_conversations INT DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tool execution logs
CREATE TABLE IF NOT EXISTS tool_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    tool_name VARCHAR(100) NOT NULL,
    parameters JSONB,
    result JSONB,
    success BOOLEAN,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tool_logs_user ON tool_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_logs_tool ON tool_logs(tool_name);

-- Vector search indexes (IVFFlat)
CREATE INDEX IF NOT EXISTS idx_user_embedding ON conversations 
USING ivfflat (user_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_assistant_embedding ON conversations 
USING ivfflat (assistant_embedding vector_cosine_ops) WITH (lists = 100);

-- Insert default user for development
INSERT INTO users (user_id, preferences) 
VALUES ('dev_user', '{"language": "ko", "voice": "default"}')
ON CONFLICT (user_id) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Moonlight database initialized successfully!';
END $$;


