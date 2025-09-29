# Project Minerva API - Modular Architecture

## Overview

The Project Minerva API has been refactored from a single monolithic `integrated_server.py` file into a well-organized modular architecture for better maintainability, scalability, and code organization.

## Directory Structure

```
api/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py          # Application configuration and settings
├── models/
│   ├── __init__.py
│   ├── requests.py          # Pydantic request models
│   └── responses.py         # Pydantic response models
├── services/
│   ├── __init__.py
│   ├── bigquery_client.py   # BigQuery operations and client
│   └── analysis_service.py  # AI analysis service and workflow
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Authentication endpoints
│   ├── startups.py         # Startup CRUD operations
│   ├── analysis.py         # Analysis endpoints and streaming
│   └── dashboard.py        # Dashboard statistics and insights
└── utils/
    ├── __init__.py
    ├── json_utils.py       # JSON parsing utilities
    └── auth.py             # Authentication utilities

main.py                     # Main FastAPI application
run_integrated_server.py    # Server startup script
integrated_server_backup.py # Backup of original monolithic file
```

## Module Breakdown

### 1. Configuration (`api/config/`)
- **`settings.py`**: Centralized configuration management
  - Google Cloud credentials setup
  - API configuration (title, description, version)
  - CORS settings
  - BigQuery configuration
  - Demo user credentials

### 2. Data Models (`api/models/`)
- **`requests.py`**: Pydantic models for API requests
  - `LoginRequest`
  - `StartupSubmissionRequest`
  - `UserRegistrationRequest`
- **`responses.py`**: Pydantic models for API responses
  - `UserResponse`
  - `LoginResponse`
  - `StartupResponse`
  - `AnalysisResponse`
  - `DashboardStatsResponse`
  - `HealthResponse`

### 3. Services (`api/services/`)
- **`bigquery_client.py`**: BigQuery operations wrapper
  - Client initialization and connection management
  - Query execution with parameter binding
  - Row insertion with error handling
  - Availability checking
- **`analysis_service.py`**: AI analysis workflow management
  - Real AI agent integration (Project Minerva agents)
  - Analysis state management
  - Event processing and result extraction
  - Simulation fallback
  - BigQuery data persistence

### 4. API Routes (`api/routes/`)
- **`auth.py`**: Authentication endpoints
  - `/api/auth/login` - User login
  - `/api/auth/register` - User registration
  - `/api/auth/logout` - User logout
  - `/api/auth/me` - Get current user
- **`startups.py`**: Startup management endpoints
  - `POST /api/startups` - Create startup
  - `GET /api/startups` - List startups (role-based)
  - `GET /api/startups/{id}` - Get startup details
  - `DELETE /api/startups/{id}` - Delete startup
- **`analysis.py`**: Analysis endpoints
  - `GET /api/analysis` - List analyses
  - `GET /api/analysis/{id}` - Get analysis details
  - `GET /api/analysis/{id}/progress` - Real-time progress
  - `GET /api/analysis/{id}/stream` - Server-sent events stream
  - `GET /api/analysis/{id}/traces` - Agent execution traces
  - `GET /api/analysis/{id}/sources` - Analysis sources
- **`dashboard.py`**: Dashboard endpoints
  - `GET /api/dashboard/stats` - Dashboard statistics
  - `GET /api/dashboard/activity` - Recent activity
  - `GET /api/dashboard/insights` - Dashboard insights

### 5. Utilities (`api/utils/`)
- **`json_utils.py`**: JSON processing utilities
  - `extract_json_from_text()` - Extract JSON from markdown/text
  - `safe_json_loads()` - Safe JSON parsing with fallbacks
- **`auth.py`**: Authentication utilities
  - `get_current_user_from_token()` - Token-based user authentication

## Key Features

### ✅ **Modular Architecture**
- Clear separation of concerns
- Easy to maintain and extend
- Reusable components
- Better testing capabilities

### ✅ **Backward Compatibility**
- All existing API endpoints preserved
- Same functionality as monolithic version
- Compatible with existing frontend

### ✅ **Enhanced Error Handling**
- Comprehensive error logging
- Graceful fallbacks
- Detailed error messages
- Type safety with Pydantic models

### ✅ **Real AI Integration**
- Project Minerva agent system integration
- Parallel agent execution
- Event-driven processing
- BigQuery data persistence
- Simulation fallback for reliability

### ✅ **Production Ready**
- Proper logging configuration
- Environment-based settings
- Health check endpoints
- CORS configuration
- Role-based access control

## Migration Benefits

1. **Maintainability**: Code is now organized into logical modules, making it easier to understand and modify
2. **Scalability**: New features can be added without affecting existing code
3. **Testing**: Individual modules can be tested in isolation
4. **Collaboration**: Multiple developers can work on different modules simultaneously
5. **Debugging**: Issues can be isolated to specific modules
6. **Documentation**: Each module has clear responsibilities and interfaces

## Usage

### Starting the Server
```bash
# Using the startup script (recommended)
python run_integrated_server.py

# Or directly
python main.py
```

### Key Imports
```python
# Configuration
from api.config import settings

# Services
from api.services import bq_client, analysis_service

# Models
from api.models import LoginRequest, StartupResponse

# Utilities
from api.utils import extract_json_from_text, get_current_user_from_token
```

## Future Enhancements

The modular architecture makes it easy to add:
- Database abstraction layer
- Caching services
- Message queues
- Additional AI models
- Enhanced authentication
- API versioning
- Rate limiting
- Monitoring and metrics

## Compatibility

- ✅ All existing API endpoints work unchanged
- ✅ Frontend requires no modifications
- ✅ BigQuery integration preserved
- ✅ Real AI agent system fully functional
- ✅ Authentication and authorization maintained
