-- =============================================================================
-- Create Database Tables for Solar PV LLM AI
-- =============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Solar PV systems table
CREATE TABLE IF NOT EXISTS solar_pv_systems (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    capacity_kw DECIMAL(10, 2),
    panel_count INTEGER,
    inverter_type VARCHAR(100),
    installation_date DATE,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Solar PV data (time-series)
CREATE TABLE IF NOT EXISTS solar_pv_data (
    id BIGSERIAL PRIMARY KEY,
    system_id INTEGER REFERENCES solar_pv_systems(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    power_output_kw DECIMAL(10, 3),
    voltage_v DECIMAL(10, 2),
    current_a DECIMAL(10, 2),
    temperature_c DECIMAL(5, 2),
    irradiance_w_m2 DECIMAL(10, 2),
    efficiency_percent DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on timestamp for faster time-series queries
CREATE INDEX idx_solar_pv_data_timestamp ON solar_pv_data(timestamp DESC);
CREATE INDEX idx_solar_pv_data_system_id ON solar_pv_data(system_id);

-- ML models registry
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(100),
    description TEXT,
    artifact_path VARCHAR(500),
    metrics JSONB,
    hyperparameters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

-- Training jobs table
CREATE TABLE IF NOT EXISTS training_jobs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) DEFAULT 'training',
    status VARCHAR(50) DEFAULT 'pending',
    training_data_path VARCHAR(500),
    hyperparameters JSONB,
    metrics JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAG documents table
CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    title VARCHAR(500),
    source_url VARCHAR(1000),
    document_type VARCHAR(100),
    content TEXT,
    metadata JSONB,
    chunk_count INTEGER DEFAULT 0,
    indexed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAG chunks table (for vector storage metadata)
CREATE TABLE IF NOT EXISTS rag_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_tokens INTEGER,
    vector_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster chunk retrieval
CREATE INDEX idx_rag_chunks_document_id ON rag_chunks(document_id);
CREATE INDEX idx_rag_chunks_vector_id ON rag_chunks(vector_id);

-- Citations table
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    query_id UUID NOT NULL,
    document_id INTEGER REFERENCES rag_documents(id),
    chunk_id BIGINT REFERENCES rag_chunks(id),
    relevance_score DECIMAL(5, 4),
    page_number INTEGER,
    cited_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    system_id INTEGER REFERENCES solar_pv_systems(id) ON DELETE CASCADE,
    model_id INTEGER REFERENCES ml_models(id),
    prediction_type VARCHAR(100),
    prediction_timestamp TIMESTAMP NOT NULL,
    predicted_value DECIMAL(10, 3),
    confidence_score DECIMAL(5, 4),
    actual_value DECIMAL(10, 3),
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_timestamp ON predictions(prediction_timestamp DESC);
CREATE INDEX idx_predictions_system_id ON predictions(system_id);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database tables created successfully';
END $$;
