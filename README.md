# 🐺 WolfAlert - AI Intelligence Dashboard

**Transforms AI news into actionable business insights for utility and technology professionals**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)

## 🎯 Project Status

**Current Phase**: Week 1-2 Development (Foundation & AI Integration)
- ✅ **Database Models**: Complete with Alembic migrations
- ✅ **Backend Structure**: FastAPI with database connectivity
- ✅ **Railway Deployment**: Backend deployed and accessible
- ⚠️ **Frontend**: In development (Next.js structure in place)
- ⚠️ **AI Integration**: Backend ready, OpenAI integration pending
- ❌ **Content Pipeline**: RSS fetching and analysis not yet implemented

**Live Demo**: https://wolfalert.app (Backend API functional, Frontend in development)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│   [IN DEV]      │    │   [DEPLOYED]    │    │                 │
│ • Dashboard     │    │ • Database      │    │ • OpenAI API    │
│ • Profile Mgmt  │    │ • API Routes    │    │ • RSS Sources   │
│ • Alert Cards   │    │ • Health Check  │    │ • PostgreSQL    │
│ • Report Gen    │    │ • Migrations    │    │ • Redis Cache   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Current System Overview

WolfAlert is an AI-powered intelligence dashboard that delivers personalized relevance analysis of AI developments. Instead of overwhelming users with generic tech news, WolfAlert shows 3-5 highly relevant alerts with clear reasoning why they matter to specific roles, departments, and industries.

### Implemented Features ✅

- **Database Schema**: Complete with user profiles, articles, insights, and RSS sources
- **Backend API Foundation**: FastAPI with health checks and database connectivity
- **Railway Deployment**: Backend deployed with PostgreSQL and Redis
- **Migration System**: Alembic for database version control
- **TypeScript Types**: Frontend type definitions established

### In Development 🚧

- **Frontend Dashboard**: Next.js 14 with Tailwind CSS
- **AI Integration**: OpenAI GPT-4o-mini for content analysis
- **RSS Content Pipeline**: Automated article fetching and processing
- **User Profile Management**: Multi-profile intelligence system
- **Alert Generation**: AI-powered relevance scoring

### Planned Features 📋

- **Report Generation**: Compile insights into executive briefings
- **Real-Time Updates**: Live RSS feeds from 40+ AI news sources
- **Impact Analysis**: THREAT/OPPORTUNITY/WATCH classification
- **Mobile Experience**: Responsive design for all devices

## 🔧 Current Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ (or Railway-provided)
- Redis 7+ (or Railway-provided)
- OpenAI API Key (for AI features)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/wolfalert.git
   cd wolfalert
   ```

2. **Backend Setup (Currently Functional)**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Set environment variables
   cp .env.example .env
   # Edit .env with your DATABASE_URL and other configs
   
   # Run migrations (if needed locally)
   alembic upgrade head
   
   # Start backend server
   python main.py
   # or: uvicorn src.main:app --reload
   ```

3. **Frontend Setup (In Development)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access Points**
   - **Production Backend**: https://wolfalert.app (Railway deployment)
   - **Local Backend**: http://localhost:8000
   - **Backend API Docs**: https://wolfalert.app/docs
   - **Local Frontend**: http://localhost:3000 (when running)

## 📊 Current Project Structure

```
wolfalert/
├── backend/                 # FastAPI application [DEPLOYED]
│   ├── src/
│   │   ├── models/          # Database models ✅
│   │   ├── api/             # API routes (partial) ⚠️
│   │   ├── services/        # Business logic (planned) ❌
│   │   └── core/            # Configuration ✅
│   ├── alembic/             # Database migrations ✅
│   ├── requirements.txt     # Dependencies ✅
│   ├── main.py             # Application entry ✅
│   └── railway.json        # Railway deployment config ✅
├── frontend/                # Next.js application [IN DEV]
│   ├── src/
│   │   ├── app/             # App router pages ⚠️
│   │   ├── components/      # UI components (planned) ❌
│   │   ├── types/           # TypeScript definitions ✅
│   │   └── utils/           # Frontend utilities (planned) ❌
│   ├── package.json         # Dependencies ✅
│   ├── next.config.js       # Next.js configuration ✅
│   └── tailwind.config.js   # Styling configuration (planned) ❌
├── railway.json             # Main deployment config ✅
└── README.md               # This file ✅
```

## 🔗 API Endpoints (Current)

### Health & Status
- `GET /health` - Service health check ✅
- `GET /api/test-db` - Database connectivity test ✅

### Profiles (Planned)
- `GET /api/profiles` - List user profiles ⚠️
- `POST /api/profiles` - Create new profile ⚠️
- `GET /api/profiles/{id}` - Get specific profile ⚠️

### Dashboard (Planned)
- `GET /api/dashboard/{profile_id}` - Get dashboard data ❌

## 🌐 Railway Deployment Status

### Current Services ✅
- **PostgreSQL Database**: Deployed and connected
- **Redis Cache**: Deployed and available
- **Backend API**: Live at https://wolfalert.app
- **Health Monitoring**: `/health` endpoint active

### Environment Variables (Required)
```bash
# Database (auto-provided by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Application Settings
OPENAI_API_KEY=sk-...         # [REQUIRED FOR AI FEATURES]
JWT_SECRET_KEY=...            # [PLANNED FOR AUTH]

# Railway Settings (auto-configured)
PORT=8000
```

### Deployment Commands
```bash
# Railway deployment is automatic via GitHub integration
# Manual deployment:
railway login
railway deploy

# Check deployment status
railway status
```

## 📋 Development Roadmap

### Week 1-2: Foundation (Current Phase)
- ✅ Database schema and migrations
- ✅ Basic API structure  
- ✅ Railway deployment
- 🚧 OpenAI integration
- 🚧 RSS content pipeline

### Week 3: Frontend Implementation
- ❌ Dashboard interface
- ❌ Profile management
- ❌ Alert card components
- ❌ Mobile responsive design

### Week 4: Integration & Demo
- ❌ Frontend-backend integration
- ❌ Live content processing
- ❌ Demo data preparation
- ❌ Performance optimization

## 🐛 Known Issues & Limitations

1. **Frontend Not Deployed**: Only backend is currently live
2. **AI Features Pending**: OpenAI integration not yet implemented  
3. **No Content Pipeline**: RSS fetching and analysis not functional
4. **Limited API Routes**: Only basic health checks currently working
5. **No Authentication**: Session-based profiles planned but not implemented

## 🤝 Contributing

This is an active development project. Current focus areas:

1. **OpenAI Integration**: Implement AI analysis pipeline
2. **RSS Pipeline**: Build content fetching and processing
3. **Frontend Development**: Complete Next.js dashboard
4. **API Routes**: Implement profile and dashboard endpoints

## 📞 Support & Development

- **Live Backend**: https://wolfalert.app
- **API Documentation**: https://wolfalert.app/docs
- **GitHub Repository**: [Your Repository URL]
- **Development Status**: Week 1-2 of 4-week MVP timeline

---

**🎯 Target Demo Date**: End of 4-week development cycle
**💼 Purpose**: NISC interview demonstration  
**🔧 Current Focus**: Backend API development and AI integration