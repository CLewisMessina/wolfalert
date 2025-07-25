# 🐺 WolfAlert - AI Intelligence Dashboard

**Transforms AI news into actionable business insights for utility and technology professionals**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)

## 🎯 Overview

WolfAlert is an AI-powered intelligence dashboard that delivers personalized relevance analysis of AI developments. Instead of overwhelming users with generic tech news, WolfAlert shows 3-5 highly relevant alerts with clear reasoning why they matter to specific roles, departments, and industries.

### Key Features

- **Multi-Profile Intelligence**: Create profiles for different roles (IT Director, Marketing Manager, etc.)
- **Impact-First Analysis**: Lead with "why this matters" before technical details
- **AI-Powered Relevance**: OpenAI GPT-4o-mini analyzes content for business impact
- **Report Generation**: Compile insights into executive briefings
- **Real-Time Updates**: RSS feeds from 40+ high-quality AI news sources

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • RSS Fetcher   │    │ • OpenAI API    │
│ • Profile Mgmt  │    │ • AI Analyzer   │    │ • RSS Sources   │
│ • Alert Cards   │    │ • API Routes    │    │ • PostgreSQL    │
│ • Report Gen    │    │ • Background    │    │ • Redis Cache   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- OpenAI API Key

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/wolfalert.git
   cd wolfalert
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Run database migrations
   alembic upgrade head
   
   # Start backend server
   uvicorn src.main:app --reload
   ```

4. **Set up frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📊 Project Structure

```
wolfalert/
├── frontend/                 # Next.js 14 application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── types/           # TypeScript definitions
│   │   └── utils/           # Frontend utilities
│   ├── tailwind.config.js   # Wolf theme configuration
│   └── package.json
├── backend/                 # FastAPI application
│   ├── src/
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic (RSS, AI, etc.)
│   │   ├── api/             # API routes
│   │   └── core/            # Configuration
│   ├── requirements.txt
│   └── main.py
├── .env.example             # Environment template
├── railway.json             # Railway deployment config
└── README.md
```

## 🔧 Development

### Database Operations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend formatting
cd backend
black src/
isort src/

# Frontend formatting
cd frontend
npm run lint
npm run type-check
```

## 🌐 Deployment

### Railway Deployment

1. **Connect GitHub repository to Railway**

2. **Configure environment variables in Railway dashboard**
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (automatically provided)
   - `REDIS_URL` (automatically provided)

3. **Deploy using Railway CLI**
   ```bash
   railway login
   railway deploy
   ```

4. **Set up custom domain**
   - Production: `wolfalert.app`
   - Development: `dev.wolfalert.app`

### Manual Deployment

```bash
# Build frontend
cd frontend
npm run build

# Start production server
cd backend
gunicorn src.main:app --workers 2 --host 0.0.0.0 --port 8000
```

## 📈 Monitoring

- **Health Check**: `GET /health`
- **API Documentation**: `/docs`
- **Error Tracking**: Sentry integration
- **Performance**: Railway metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Single Responsibility Principle
- Keep files under 400 lines
- Write tests for new features
- Update documentation
- Use conventional commit messages

## 📝 API Documentation

### Core Endpoints

- `GET /api/profiles` - List user profiles
- `POST /api/profiles` - Create new profile
- `GET /api/dashboard/{profile_id}` - Get personalized dashboard
- `POST /api/interactions` - Track user interactions
- `POST /api/reports/generate` - Generate custom report

### Example API Usage

```javascript
// Get dashboard data
const response = await fetch('/api/dashboard/1')
const dashboard = await response.json()

// Create new profile
const newProfile = await fetch('/api/profiles', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    profile_name: 'IT Director',
    industry: 'electric',
    department: 'it',
    role_level: 'director'
  })
})
```

## 🎨 Design System

### Wolf Theme Colors

```css
--wolf-primary: #0f172a     /* Dark navy background */
--wolf-accent: #6366f1      /* Indigo accent */
--wolf-bg: #0f0f23          /* Deep background */
--wolf-card: #1a1a2e        /* Card background */
--wolf-surface: #16213e     /* Surface elements */
```

### Component Classes

- `.glass-morphism` - Glassmorphism effect
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary button
- `.alert-card` - Alert card styling
- `.threat-glow` - Red glow for threats
- `.opportunity-glow` - Green glow for opportunities
- `.watch-glow` - Blue glow for watch items

## 🔍 RSS Sources

WolfAlert aggregates from 40+ high-quality sources:

- **Official Blogs**: OpenAI, Google AI, Microsoft, AWS, NVIDIA
- **News Sites**: TechCrunch AI, VentureBeat, MIT Tech Review
- **Community**: Reddit AI subs, Hacker News
- **Releases**: GitHub releases for major AI tools

## 🤖 AI Processing

### Analysis Pipeline

1. **Content Fetching** - RSS feeds every 4 hours
2. **Content Cleaning** - Extract and sanitize article text
3. **AI Analysis** - Generate summaries and impact analysis
4. **Relevance Scoring** - 0.00-1.00 score per profile
5. **Caching** - Redis cache for performance

### Prompting Strategy

```python
f"""
Analyze this AI/technology article for a {profile.role_level} 
{profile.department} professional in the {profile.industry} industry.

Generate:
1. Executive Summary (2-3 sentences)
2. Business Impact Analysis (Why this matters specifically)
3. Impact Classification: THREAT, OPPORTUNITY, or WATCH
4. Impact Score: 0.0-1.0 based on urgency and relevance
"""
```

## 📊 Performance

### Optimization Features

- **Caching**: Redis for AI responses and dashboard data
- **Database**: Connection pooling and query optimization
- **Frontend**: Next.js 14 with App Router
- **CDN**: Static asset optimization
- **Background Processing**: Celery for RSS fetching

### Performance Targets

- Dashboard load: < 3 seconds
- AI analysis: < 10 seconds per article
- RSS processing: < 30 seconds per source
- Cache hit ratio: > 80%

## 🛡️ Security

### Security Features

- **CORS Protection**: Configured origins
- **Rate Limiting**: API request limits
- **Input Validation**: Pydantic models
- **SQL Injection**: Parameterized queries
- **XSS Prevention**: Content sanitization

### Environment Security

```bash
# Required environment variables
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://...
```

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) for GPT-4o-mini API
- [Railway](https://railway.app) for deployment platform
- [Next.js](https://nextjs.org) team for the amazing framework
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [Tailwind CSS](https://tailwindcss.com) for styling

## 📞 Support

- **Email**: support@wolfalert.app
- **Documentation**: [docs.wolfalert.app](https://docs.wolfalert.app)
- **Issues**: [GitHub Issues](https://github.com/your-username/wolfalert/issues)

---

**Built with ❤️ for utility and technology professionals**