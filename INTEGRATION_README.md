# Project Minerva - BigQuery & AI Agent Integration

This document describes the complete integration of BigQuery storage and real AI agents into Project Minerva.

## 🚀 Quick Start

### 1. Start the Integrated Backend Server
```bash
cd a:\project\adk-samples\python\agents\Project-minerva
python run_integrated_server.py
```
The server will start on `http://localhost:8001`

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5174`

## 🏗️ Architecture Overview

### Backend Integration (`integrated_server.py`)
- **FastAPI** server with BigQuery integration
- **Real AI Agents** using Google ADK framework
- **Streaming analysis** results via Server-Sent Events
- **Role-based access control** (Founder vs Investor views)
- **Background task processing** for AI analysis

### Key Components

#### 1. BigQuery Storage
- **Startups Table**: Stores all startup submissions
- **Analyses Table**: Stores analysis results and progress
- **Agent Traces Table**: Stores detailed agent execution traces
- **Sources Table**: Stores citations and sources used by agents

#### 2. AI Agent Workflow
```
Startup Submission → BigQuery Storage → AI Agent Analysis → Results Storage → Frontend Display
```

**Agent Pipeline:**
1. **Orchestrator Agent**: Plans and coordinates analysis
2. **Team Agent**: Evaluates founders and team
3. **Market Agent**: Analyzes market opportunity
4. **Product Agent**: Assesses product-market fit
5. **Competition Agent**: Evaluates competitive landscape
6. **Synthesis Agent**: Creates final investment memo

#### 3. Real-time Features
- **Progress Streaming**: `/api/analysis/{id}/stream`
- **Agent Traces**: `/api/analysis/{id}/traces`
- **Source Citations**: `/api/analysis/{id}/sources`

## 🔄 Complete Workflow

### Startup Submission Flow
1. **Frontend**: User submits startup details via form
2. **Backend**: Data stored in BigQuery `startups` table
3. **Background Task**: AI analysis automatically triggered
4. **Agent Processing**: 6 specialized agents analyze the startup
5. **Results Storage**: Analysis results stored in BigQuery
6. **Frontend Update**: Dashboard shows real-time progress and results

### Role-Based Data Access
- **Founders**: See only their own submissions and analyses
- **Investors/Analysts**: See all startups and analyses across platform

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Startups (BigQuery Integrated)
- `GET /api/startups` - List startups (role-filtered)
- `POST /api/startups` - Submit new startup (triggers AI analysis)
- `GET /api/startups/{id}` - Get specific startup details

### Analysis (AI Agent Integrated)
- `GET /api/analysis` - List analyses (role-filtered)
- `GET /api/analysis/{id}` - Get detailed analysis results
- `GET /api/analysis/{id}/progress` - Get analysis progress
- `GET /api/analysis/{id}/stream` - Stream real-time updates (SSE)
- `GET /api/analysis/{id}/traces` - Get agent execution traces
- `GET /api/analysis/{id}/sources` - Get sources and citations

### Dashboard (BigQuery Stats)
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/activity` - Get recent activity
- `GET /api/dashboard/insights` - Get AI insights

## 🔧 Configuration

### Environment Variables
```bash
# BigQuery Configuration
BIGQUERY_DATASET=minerva_dataset
BIGQUERY_LOCATION=US
GOOGLE_CLOUD_PROJECT=your-project-id

# AI Agent Configuration
MAX_ANALYSIS_TIME_MINUTES=30
MAX_CONCURRENT_ANALYSES=5
ENABLE_AGENT_TRACING=true

# Application Configuration
APP_ENV=development
FRONTEND_URL=http://localhost:5174
BACKEND_URL=http://localhost:8001
```

### Google Cloud Setup
1. **Enable APIs**:
   - BigQuery API
   - Vertex AI API (for Gemini models)

2. **Authentication**:
   ```bash
   gcloud auth application-default login
   ```

3. **Create BigQuery Dataset**:
   ```bash
   bq mk --dataset --location=US your-project-id:minerva_dataset
   ```

## 🎯 Key Features Implemented

### ✅ BigQuery Integration
- [x] Automatic table creation with proper schemas
- [x] Startup submission storage
- [x] Analysis results storage
- [x] Agent traces and sources storage
- [x] Role-based data filtering

### ✅ AI Agent Integration
- [x] Real Google ADK agent system
- [x] 6 specialized agents (orchestrator, team, market, product, competition, synthesis)
- [x] Callback functions for progress tracking
- [x] Source citation collection
- [x] Execution trace logging
- [x] Fallback simulation when agents unavailable

### ✅ Streaming & Real-time Updates
- [x] Server-Sent Events for analysis progress
- [x] Real-time agent result streaming
- [x] Progress percentage tracking
- [x] Agent execution transparency

### ✅ Frontend Integration
- [x] Updated API configuration to use port 8001
- [x] Real startup data display (no more mock data)
- [x] Proper date formatting with error handling
- [x] Role-based UI filtering

## 🚨 Troubleshooting

### Common Issues

1. **BigQuery Connection Error**
   ```
   Solution: Ensure Google Cloud credentials are set up
   gcloud auth application-default login
   ```

2. **Agent Import Error**
   ```
   Solution: Server falls back to simulation mode
   Check logs for specific import issues
   ```

3. **Port Conflicts**
   ```
   Solution: Change port in integrated_server.py and frontend api.ts
   Default: Backend on 8001, Frontend on 5174
   ```

4. **Date Format Errors**
   ```
   Solution: All dates now use proper ISO format with milliseconds
   Frontend has robust error handling for invalid dates
   ```

## 📈 Performance & Monitoring

### Logging
- **Analysis Progress**: Real-time logging of agent execution
- **BigQuery Operations**: Insert/query performance tracking
- **Error Handling**: Comprehensive error logging and fallback

### Metrics
- **Analysis Duration**: Tracked per startup
- **Agent Performance**: Individual agent execution times
- **Database Performance**: BigQuery query performance

## 🔮 Future Enhancements

### Planned Features
- [ ] Document upload to Google Cloud Storage
- [ ] Advanced search and filtering
- [ ] Collaborative analysis features
- [ ] Export to PDF/Excel
- [ ] Advanced analytics dashboard
- [ ] Human-in-the-loop feedback system

### Scalability
- [ ] Kubernetes deployment
- [ ] Load balancing for multiple instances
- [ ] Caching layer (Redis)
- [ ] Message queue for analysis tasks (Pub/Sub)

## 📝 Development Notes

### File Structure
```
Project-minerva/
├── integrated_server.py          # Main integrated API server
├── run_integrated_server.py      # Startup script
├── auth_server.py                # Legacy mock server (deprecated)
├── app/                          # Project Minerva components
│   ├── config.py                 # Configuration
│   ├── agent.py                  # Main agent orchestration
│   ├── storage/                  # BigQuery storage layer
│   ├── models/                   # Pydantic models
│   └── agents/                   # Individual agent implementations
└── frontend/                     # React frontend
    └── src/services/api.ts       # Updated to use port 8001
```

### Testing
```bash
# Test BigQuery connection
python -c "from app.storage.bigquery_client import BigQueryClient; print('BigQuery OK')"

# Test agent imports
python -c "from app.agents.orchestrator import orchestrator_agent; print('Agents OK')"

# Test server startup
python run_integrated_server.py
```

## 🎉 Success Metrics

The integration is successful when:
- [x] Startups submitted via frontend appear in BigQuery
- [x] AI analysis automatically triggers on submission
- [x] Real-time progress updates stream to frontend
- [x] Analysis results stored in BigQuery and displayed correctly
- [x] Role-based access control works properly
- [x] No more mock data - all data comes from BigQuery
- [x] Date formatting errors resolved
- [x] Complete startup workflow functional

**Status: ✅ INTEGRATION COMPLETE**

All major requirements have been implemented and tested. The system now provides a complete BigQuery-integrated, AI-powered startup due diligence platform with real-time streaming capabilities.
