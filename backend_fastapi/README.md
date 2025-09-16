# EduLMS v2 FastAPI Backend

A modern Python backend using FastAPI, SQLAlchemy, and TiDB Serverless with vector search capabilities to replace the Strapi backend.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **TiDB Serverless**: Cloud-native MySQL-compatible database with vector search
- **SQLAlchemy**: Powerful ORM with async support
- **Google Gemini**: AI integration for embeddings and content generation
- **Multi-Agent System**: Integration with Python agents for AI workflows
- **JWT Authentication**: Secure user authentication and authorization
- **Vector Search**: Semantic search capabilities using TiDB vector extensions

## Architecture

```
backend_fastapi/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── alembic.ini            # Database migration configuration
├── alembic/               # Database migrations
├── database/
│   └── connection.py      # TiDB connection and configuration
├── models/                # SQLAlchemy models
│   ├── user.py           # User model with agent session support
│   ├── workflow.py       # Workflow orchestration model
│   ├── analytics.py      # Learning analytics model
│   ├── content.py        # Content with vector embeddings
│   └── agent_session.py  # Agent communication sessions
├── routers/               # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management
│   ├── workflows.py      # Multi-agent workflows
│   ├── agents.py         # Agent communication
│   └── analytics.py      # Learning analytics
└── services/              # Business logic services
    ├── auth_service.py    # Authentication logic
    ├── vector_service.py  # TiDB vector search
    └── agent_service.py   # Agent orchestration
```

## Setup

1. **Install Dependencies**
```bash
cd backend_fastapi
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your TiDB and Google Gemini credentials
```

3. **Initialize Database**
```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

4. **Run Development Server**
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /auth/local` - Login
- `POST /auth/local/register` - Register
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Users
- `GET /users/me` - Get user profile
- `PUT /users/me` - Update user profile
- `GET /users/{user_id}` - Get public user profile

### Workflows
- `POST /workflows/create-from-template` - Create workflow
- `GET /workflows/{id}/status` - Get workflow status
- `POST /workflows/{id}/cancel` - Cancel workflow
- `GET /workflows/{id}/logs` - Get workflow logs
- `GET /workflows` - List user workflows
- `GET /workflows/templates` - Get workflow templates

### Agents
- `POST /agents/sessions` - Create agent session
- `GET /agents/sessions/{id}` - Get agent session
- `POST /agents/sessions/{id}/message` - Send message to agent
- `POST /agents/sessions/{id}/close` - Close agent session
- `GET /agents/sessions` - List agent sessions
- `GET /agents/status` - Get agent system status
- `POST /agents/execute` - Execute direct agent action

### Analytics
- `POST /analytics/events` - Create analytics event
- `GET /analytics/user-report` - Get user analytics report
- `GET /analytics/system-report` - Get system analytics report (admin)

## TiDB Vector Search

The backend implements vector search using TiDB's vector extensions:

```python
# Generate embeddings using Google Gemini
embedding = await vector_service.generate_embedding(text)

# Store content with vector embedding
content_id = await vector_service.store_content_with_embedding(
    title="Sample Content",
    content_text="Content to be embedded",
    content_type="lesson"
)

# Perform vector similarity search
results = await vector_service.vector_search(
    query_text="search query",
    limit=10,
    content_type="lesson"
)
```

## Multi-Agent Integration

The backend integrates with the Python agents system:

```python
# Execute agent action
agent_service = AgentService()
result = await agent_service.execute_action(
    action="create_quiz",
    data={"lesson_content": "content", "difficulty": "intermediate"}
)

# Execute multi-step workflow
workflow_result = await agent_service.execute_workflow(
    workflow_id=123,
    template_name="adaptive_learning_pipeline",
    parameters={"user_id": 456, "course_id": 789}
)
```

## Database Models

### User Model
- Authentication and profile information
- Learning preferences and skill level
- Agent session management
- Role-based access control

### Workflow Model
- Multi-agent workflow orchestration
- Status tracking and progress monitoring
- Parameter and result storage
- Error handling and retry logic

### Content Model
- Vector embeddings for semantic search
- Content type classification
- Difficulty level and subject tagging
- Version control and publishing status

### Analytics Model
- Learning event tracking
- Performance metrics
- Session and workflow analytics
- User behavior analysis

## Environment Variables

```bash
# Database
TIDB_HOST=your-tidb-host
TIDB_PORT=4000
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DATABASE=edulms_v2
TIDB_SSL=true

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Integration
GOOGLE_API_KEY=your-gemini-api-key

# Application
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

## Migration from Strapi

This FastAPI backend provides full compatibility with the existing frontend:

1. **Authentication**: Same JWT-based auth with `/auth/local` endpoints
2. **User Management**: Compatible user profile structure
3. **Workflow API**: Maintains workflow template and execution patterns
4. **Agent Integration**: Direct integration with Python agents
5. **Analytics**: Enhanced analytics with vector search capabilities

## Development

### Adding New Models
1. Create model in `models/` directory
2. Import in `models/__init__.py`
3. Generate migration: `alembic revision --autogenerate -m "Description"`
4. Apply migration: `alembic upgrade head`

### Adding New Endpoints
1. Create router in `routers/` directory
2. Add business logic in `services/`
3. Include router in `main.py`
4. Update documentation

### Testing
```bash
# Run tests
pytest

# Test with coverage
pytest --cov=.

# Test specific module
pytest tests/test_auth.py
```

## Production Deployment

1. **Environment Setup**
```bash
export TIDB_HOST=production-host
export TIDB_PASSWORD=secure-password
export JWT_SECRET_KEY=production-secret
export GOOGLE_API_KEY=production-api-key
```

2. **Database Migration**
```bash
alembic upgrade head
```

3. **Run Production Server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Monitoring and Logging

- Health check endpoint: `GET /health`
- System status: `GET /agents/status`
- Analytics dashboard: `GET /analytics/system-report`
- Database connection monitoring via SQLAlchemy pool metrics

## Security

- JWT token authentication
- Password hashing with bcrypt
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for frontend integration
- Environment variable protection for secrets
