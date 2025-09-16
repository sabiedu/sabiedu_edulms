# EduLMS v2 - Intelligent Learning Management System

A comprehensive, AI-powered Learning Management System built with modern technologies and sophisticated multi-agent architecture.

## 🏗️ Architecture

EduLMS v2 features a unified architecture combining:

- **Frontend**: Nuxt 3 with TypeScript, Tailwind CSS, and composables
- **Backend**: FastAPI with SQLAlchemy, async support, and TiDB vector search
- **Database**: TiDB Serverless with vector search capabilities for semantic content discovery
- **AI Agents**: 9 specialized agents with Google Gemini integration
- **Workflows**: Multi-agent workflow orchestration with dependency management
- **Communication**: Direct Python agent integration with FastAPI backend

## 🤖 Multi-Agent System

### Specialized Agents

1. **Research Agent** - Academic research, literature review, citation management
2. **Analytics Agent** - Learning analytics, predictive modeling, performance reporting
3. **Assessment Agent** - Quiz/assignment grading with AI-powered quiz generation
4. **Tutor Agent** - Conversational tutoring with Google Gemini integration
5. **Content Generation Agent** - Automated lesson, quiz, assignment, and summary creation
6. **Personalization Agent** - Adaptive learning, user profiling, recommendation engine
7. **Content Curator Agent** - Content discovery and curation with AI assistance
8. **Learning Path Agent** - Personalized learning path generation and optimization
9. **Monitoring Agent** - System health monitoring, performance tracking, diagnostics

### Communication Architecture

- **TiDB-based messaging** - Reliable, queryable inter-agent communication
- **Database-backed caching** - Persistent agent result caching with TTL
- **Session management** - Full SQL-queryable agent interaction sessions
- **Task queuing** - Database-backed task coordination with retry mechanisms

## 🚀 Features

- **Intelligent Content Discovery** - AI-powered semantic search and content curation
- **Personalized Learning Paths** - Dynamic, adaptive learning journeys
- **Smart Assessments** - AI-generated questions with adaptive difficulty
- **Real-time Tutoring** - Personalized instruction and comprehension checking
- **Advanced Analytics** - Deep learning insights and performance analysis
- **Multi-agent Collaboration** - Seamless coordination between specialized AI agents
- **Vector Search** - Semantic content discovery using embeddings
- **Workflow Orchestration** - Prefect-managed multi-agent workflows

## 📁 Project Structure

```
edulms-v2/
├── agents/                 # Multi-agent system
│   ├── specialized/       # 9 AI agent implementations
│   ├── communication/     # TiDB communication services
│   ├── workflows/         # Multi-agent orchestration
│   └── config/           # Agent configuration
├── backend_fastapi/      # FastAPI backend with TiDB vector search
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API route handlers
│   ├── services/        # Business logic services
│   ├── database/        # TiDB connection and migrations
│   └── alembic/         # Database migrations
├── frontend/            # Nuxt 3 frontend application
│   ├── components/      # Vue components
│   ├── pages/          # Application pages
│   └── composables/    # Nuxt composables
├── scripts/            # Deployment and utility scripts
├── tests/             # Testing suite
└── docker-compose.yml # Development environment setup
```

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for agent development)

### 🚀 Start Services

#### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Update .env with your TiDB password:
# TIDB_PASSWORD=your-actual-password
```

#### 2. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### 3. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### 4. Test Multi-Agent System
Visit the frontend and navigate to:
- `/chat` - Tutor Agent
- `/analytics` - Analytics Agent  
- `/assessments` - Assessment Agent
- `/research` - Research Agent
- `/workflows` - Multi-Agent Workflows

## 🔧 Configuration

### Environment Variables (.env)
- **TiDB Serverless**: Database connection with SSL
- **Google Gemini API**: AI model integration  
- **Strapi**: Backend authentication and security
- **Frontend URLs**: Local development endpoints

### TiDB Serverless Integration
The system connects directly to TiDB Serverless for:
- Multi-agent communication and coordination
- Vector embeddings for semantic search
- Educational content and user data
- Workflow state management

## 🧪 Development

### Backend Development
```bash
cd backend
npm install
npm run develop
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Agent Development
```bash
cd agents
pip install -e .
python -m agents.main
```

### Testing
```bash
# Backend tests
cd backend && npm test

# Frontend tests
cd frontend && npm test

# Agent tests
cd agents && pytest
```

## 📊 Monitoring

- **Prefect UI**: Workflow monitoring and management
- **Agent Metrics**: Performance and health monitoring
- **Database Analytics**: Query performance and usage statistics
- **Application Logs**: Comprehensive logging across all services

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Secure agent communication
- Input sanitization and validation
- API rate limiting
- Comprehensive audit logging

## 📚 Documentation

- [Agent System Documentation](agents/README.md)
- [Backend API Documentation](backend/README.md)
- [Frontend Development Guide](frontend/README.md)
- [Database Schema](database/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.