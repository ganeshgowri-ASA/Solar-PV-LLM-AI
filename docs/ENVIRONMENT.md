# Environment Variables Documentation

This document provides comprehensive documentation for all environment variables used in the Solar PV LLM AI project.

## Table of Contents

- [Quick Setup](#quick-setup)
- [Application Settings](#application-settings)
- [AI/LLM Configuration](#aillm-configuration)
- [Database Configuration](#database-configuration)
- [Security & Authentication](#security--authentication)
- [Logging & Monitoring](#logging--monitoring)
- [RAG Configuration](#rag-configuration)
- [Best Practices](#best-practices)

## Quick Setup

1. Copy the template file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your preferred text editor
3. Fill in required values (marked with ⚠️ below)
4. Restart services to apply changes

## Application Settings

### `APP_ENV`
- **Type**: String
- **Default**: `development`
- **Options**: `development`, `staging`, `production`
- **Description**: Application environment mode
- **Example**: `APP_ENV=production`

### `APP_PORT`
- **Type**: Integer
- **Default**: `8000`
- **Description**: Port on which the backend API server runs
- **Example**: `APP_PORT=8000`

### `APP_HOST`
- **Type**: String (IP address)
- **Default**: `0.0.0.0`
- **Description**: Host address for the API server
- **Example**: `APP_HOST=0.0.0.0`

### `DEBUG`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable/disable debug mode (auto-reload, verbose logging)
- **Example**: `DEBUG=false`
- **Note**: Set to `false` in production!

## AI/LLM Configuration

### OpenAI Configuration

#### `OPENAI_API_KEY` ⚠️
- **Type**: String (API Key)
- **Required**: Yes
- **Description**: OpenAI API key for GPT models
- **How to get**: https://platform.openai.com/api-keys
- **Example**: `OPENAI_API_KEY=sk-proj-abc123...`
- **Security**: Never commit this value!

#### `OPENAI_MODEL`
- **Type**: String
- **Default**: `gpt-4`
- **Options**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Description**: OpenAI model to use for completions
- **Example**: `OPENAI_MODEL=gpt-4-turbo`

#### `OPENAI_MAX_TOKENS`
- **Type**: Integer
- **Default**: `2000`
- **Range**: `1` to `128000` (model-dependent)
- **Description**: Maximum tokens in model responses
- **Example**: `OPENAI_MAX_TOKENS=4000`

#### `OPENAI_TEMPERATURE`
- **Type**: Float
- **Default**: `0.7`
- **Range**: `0.0` to `2.0`
- **Description**: Controls randomness in responses (0 = deterministic, 2 = creative)
- **Example**: `OPENAI_TEMPERATURE=0.3`

### Anthropic Claude Configuration

#### `ANTHROPIC_API_KEY` ⚠️
- **Type**: String (API Key)
- **Required**: Yes
- **Description**: Anthropic API key for Claude models
- **How to get**: https://console.anthropic.com/
- **Example**: `ANTHROPIC_API_KEY=sk-ant-api03-...`
- **Security**: Never commit this value!

#### `ANTHROPIC_MODEL`
- **Type**: String
- **Default**: `claude-3-sonnet-20240229`
- **Options**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Description**: Anthropic Claude model to use
- **Example**: `ANTHROPIC_MODEL=claude-3-opus-20240229`

#### `ANTHROPIC_MAX_TOKENS`
- **Type**: Integer
- **Default**: `4000`
- **Range**: `1` to `200000`
- **Description**: Maximum tokens in Claude responses
- **Example**: `ANTHROPIC_MAX_TOKENS=8000`

### Pinecone Vector Database

#### `PINECONE_API_KEY` ⚠️
- **Type**: String (API Key)
- **Required**: Yes
- **Description**: Pinecone API key for vector database access
- **How to get**: https://app.pinecone.io/
- **Example**: `PINECONE_API_KEY=abc123-def456-...`
- **Security**: Never commit this value!

#### `PINECONE_ENVIRONMENT` ⚠️
- **Type**: String
- **Required**: Yes
- **Description**: Pinecone environment/region
- **Example**: `PINECONE_ENVIRONMENT=us-east1-gcp`
- **Note**: Must match your Pinecone index configuration

#### `PINECONE_INDEX_NAME`
- **Type**: String
- **Default**: `solar-pv-embeddings`
- **Description**: Name of the Pinecone index to use
- **Example**: `PINECONE_INDEX_NAME=solar-pv-prod`

#### `PINECONE_DIMENSION`
- **Type**: Integer
- **Default**: `1536`
- **Description**: Vector dimension size (must match embedding model)
- **Example**: `PINECONE_DIMENSION=1536`
- **Note**: OpenAI ada-002 uses 1536 dimensions

### NREL API

#### `NREL_API_KEY` ⚠️
- **Type**: String (API Key)
- **Required**: Yes
- **Description**: National Renewable Energy Laboratory API key
- **How to get**: https://developer.nrel.gov/signup/
- **Example**: `NREL_API_KEY=your_nrel_key_here`
- **Security**: Can be committed if using demo key, but use secrets in production

#### `NREL_BASE_URL`
- **Type**: String (URL)
- **Default**: `https://developer.nrel.gov/api`
- **Description**: Base URL for NREL API endpoints
- **Example**: `NREL_BASE_URL=https://developer.nrel.gov/api`

## Database Configuration

### PostgreSQL

#### `DATABASE_URL`
- **Type**: String (Connection URL)
- **Default**: `postgresql://user:password@localhost:5432/solar_pv_db`
- **Description**: Full PostgreSQL connection string
- **Example**: `DATABASE_URL=postgresql://solar_user:secure_pass@db.example.com:5432/solar_pv`
- **Format**: `postgresql://[user]:[password]@[host]:[port]/[database]`

#### `POSTGRES_USER`
- **Type**: String
- **Default**: `solar_user`
- **Description**: PostgreSQL username
- **Example**: `POSTGRES_USER=solar_user`

#### `POSTGRES_PASSWORD` ⚠️
- **Type**: String
- **Required**: Yes (for production)
- **Description**: PostgreSQL password
- **Example**: `POSTGRES_PASSWORD=super_secure_password_123`
- **Security**: Use strong passwords in production!

#### `POSTGRES_DB`
- **Type**: String
- **Default**: `solar_pv_db`
- **Description**: PostgreSQL database name
- **Example**: `POSTGRES_DB=solar_pv_production`

#### `POSTGRES_HOST`
- **Type**: String (hostname/IP)
- **Default**: `localhost`
- **Description**: PostgreSQL server hostname
- **Example**: `POSTGRES_HOST=postgres` (in Docker)

#### `POSTGRES_PORT`
- **Type**: Integer
- **Default**: `5432`
- **Description**: PostgreSQL server port
- **Example**: `POSTGRES_PORT=5432`

### Redis Cache

#### `REDIS_HOST`
- **Type**: String (hostname/IP)
- **Default**: `localhost`
- **Description**: Redis server hostname
- **Example**: `REDIS_HOST=redis` (in Docker)

#### `REDIS_PORT`
- **Type**: Integer
- **Default**: `6379`
- **Description**: Redis server port
- **Example**: `REDIS_PORT=6379`

#### `REDIS_PASSWORD`
- **Type**: String
- **Default**: Empty
- **Description**: Redis authentication password
- **Example**: `REDIS_PASSWORD=redis_secure_pass`
- **Security**: Set a password in production!

#### `REDIS_DB`
- **Type**: Integer
- **Default**: `0`
- **Range**: `0` to `15`
- **Description**: Redis database number
- **Example**: `REDIS_DB=0`

## Frontend Configuration

### `FRONTEND_PORT`
- **Type**: Integer
- **Default**: `3000`
- **Description**: Port on which the frontend development server runs
- **Example**: `FRONTEND_PORT=3000`

### `VITE_API_URL`
- **Type**: String (URL)
- **Default**: `http://localhost:8000`
- **Description**: Backend API URL for frontend to connect to
- **Example**: `VITE_API_URL=https://api.solarpv.example.com`
- **Note**: Must start with `VITE_` to be exposed to frontend

### `VITE_APP_NAME`
- **Type**: String
- **Default**: `Solar PV LLM AI`
- **Description**: Application name displayed in frontend
- **Example**: `VITE_APP_NAME=Solar PV AI - Production`

## Security & Authentication

### `JWT_SECRET` ⚠️
- **Type**: String
- **Required**: Yes
- **Description**: Secret key for JWT token signing
- **Example**: `JWT_SECRET=your-256-bit-secret-key-here`
- **Security**: Generate with `openssl rand -hex 32`
- **Note**: Changing this invalidates all existing tokens!

### `JWT_EXPIRATION`
- **Type**: Integer (seconds)
- **Default**: `3600` (1 hour)
- **Description**: JWT token expiration time in seconds
- **Example**: `JWT_EXPIRATION=7200` (2 hours)

### `CORS_ORIGINS`
- **Type**: String (comma-separated URLs)
- **Default**: `http://localhost:3000,http://localhost:8000`
- **Description**: Allowed CORS origins for API requests
- **Example**: `CORS_ORIGINS=https://app.example.com,https://admin.example.com`
- **Security**: Be specific in production, avoid wildcards!

## Logging & Monitoring

### `LOG_LEVEL`
- **Type**: String
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description**: Minimum log level to record
- **Example**: `LOG_LEVEL=WARNING`

### `LOG_FORMAT`
- **Type**: String
- **Default**: `json`
- **Options**: `json`, `text`
- **Description**: Log output format
- **Example**: `LOG_FORMAT=json`
- **Note**: JSON format recommended for production

## AI/ML Model Settings

### `EMBEDDING_MODEL`
- **Type**: String
- **Default**: `text-embedding-ada-002`
- **Description**: OpenAI embedding model for vector generation
- **Example**: `EMBEDDING_MODEL=text-embedding-3-large`

### `CHUNK_SIZE`
- **Type**: Integer
- **Default**: `1000`
- **Description**: Text chunk size for document processing (characters)
- **Example**: `CHUNK_SIZE=1500`

### `CHUNK_OVERLAP`
- **Type**: Integer
- **Default**: `200`
- **Description**: Overlap between chunks (characters)
- **Example**: `CHUNK_OVERLAP=300`
- **Note**: Should be 10-20% of CHUNK_SIZE

### `MAX_CONTEXT_LENGTH`
- **Type**: Integer
- **Default**: `8000`
- **Description**: Maximum context length for LLM prompts (tokens)
- **Example**: `MAX_CONTEXT_LENGTH=16000`

## RAG Configuration

### `RAG_TOP_K`
- **Type**: Integer
- **Default**: `5`
- **Range**: `1` to `100`
- **Description**: Number of top results to retrieve from vector database
- **Example**: `RAG_TOP_K=10`

### `RAG_SIMILARITY_THRESHOLD`
- **Type**: Float
- **Default**: `0.7`
- **Range**: `0.0` to `1.0`
- **Description**: Minimum similarity score for retrieval results
- **Example**: `RAG_SIMILARITY_THRESHOLD=0.75`
- **Note**: Higher = stricter relevance filtering

### `ENABLE_CITATIONS`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Include source citations in LLM responses
- **Example**: `ENABLE_CITATIONS=true`

## Data Source Configuration

### `DATA_REFRESH_INTERVAL`
- **Type**: Integer (seconds)
- **Default**: `86400` (24 hours)
- **Description**: Interval for automatic data source refresh
- **Example**: `DATA_REFRESH_INTERVAL=43200` (12 hours)

### `ENABLE_AUTO_SYNC`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable automatic synchronization of external data sources
- **Example**: `ENABLE_AUTO_SYNC=true`
- **Note**: Set to `false` to control syncing manually

## Best Practices

### Development Environment

```bash
# .env for local development
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Use test/demo API keys or create separate dev accounts
OPENAI_API_KEY=sk-test-...
ANTHROPIC_API_KEY=sk-ant-test-...
```

### Staging Environment

```bash
# .env for staging
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO

# Use separate staging API keys with rate limits
# Test production-like configuration
```

### Production Environment

```bash
# .env for production
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json

# Use secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
# Never commit production .env file
# Use strong passwords and rotate regularly
# Enable all security features
# Monitor API usage and costs
```

### Security Checklist

- [ ] All API keys are valid and have appropriate permissions
- [ ] `JWT_SECRET` is cryptographically random (32+ characters)
- [ ] Database passwords are strong (16+ characters, mixed case, symbols)
- [ ] `DEBUG=false` in production
- [ ] `CORS_ORIGINS` is specific (no wildcards in production)
- [ ] `.env` file is in `.gitignore`
- [ ] Use secrets management service in production
- [ ] Rotate secrets regularly
- [ ] Monitor for unauthorized access
- [ ] Enable rate limiting on APIs

### Generating Secure Secrets

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate database password
openssl rand -base64 24

# Generate Redis password
openssl rand -base64 16
```

## Troubleshooting

### Common Issues

**Issue**: Environment variables not loading
- **Solution**: Restart application/containers after changing `.env`
- **Check**: File is named `.env` (not `.env.txt` or similar)
- **Verify**: File is in the project root directory

**Issue**: API authentication failures
- **Solution**: Verify API keys are valid and active
- **Check**: No extra spaces or quotes in `.env` values
- **Test**: Use API key in official provider's playground first

**Issue**: Database connection errors
- **Solution**: Verify `DATABASE_URL` format is correct
- **Check**: Database service is running (`docker-compose ps`)
- **Test**: Connect manually using `psql` or database client

**Issue**: CORS errors in browser
- **Solution**: Add frontend URL to `CORS_ORIGINS`
- **Check**: No trailing slashes in URLs
- **Format**: Comma-separated, no spaces

## Environment Variable Precedence

1. **System environment variables** (highest priority)
2. **`.env` file in project root**
3. **Default values in code** (lowest priority)

To override `.env` values temporarily:

```bash
# Override for single command
OPENAI_MODEL=gpt-3.5-turbo python app/main.py

# Override for Docker container
docker-compose run -e OPENAI_MODEL=gpt-3.5-turbo backend python app/main.py
```

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [NREL Developer Network](https://developer.nrel.gov/)
- [FastAPI Settings Management](https://fastapi.tiangolo.com/advanced/settings/)

---

Last updated: 2025-11-18
