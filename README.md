# Project Younicorn - AI-Powered Startup Due Diligence Platform

Project Younicorn is a sophisticated AI-powered platform that automates startup due diligence for investors using a multi-agent AI engine that transforms raw founder materials into an interactive, analytical dashboard.

## 🚀 Project Vision & Workflow

The platform consists of two main portals with an asynchronous backend workflow:

### Founder Portal
- Secure and intuitive interface for startup founders
- Submit pitch decks, financial documents, business plans
- Upload links to websites or product demos
- Real-time submission status tracking

### Asynchronous AI Analysis
- Background processing by specialized AI agents
- Fast and responsive user interface
- Notification system when analysis is complete
- Multi-agent orchestration for comprehensive analysis

### Investor Portal
- Comprehensive dashboard for AI-generated analysis
- Team collaboration features
- Direct AI interaction capabilities
- Investment decision support tools


<img width="3440" height="1808" alt="localhost_5173_auth_login (1)" src="https://github.com/user-attachments/assets/ac81d5a8-9506-4e0d-928f-3b8fa7acf6cb" />
<img width="3456" height="1782" alt="localhost_5173_auth_login (2)" src="https://github.com/user-attachments/assets/0050c2b4-2bef-4ac5-95a0-02c16410a49a" />
<img width="3456" height="5432" alt="screencapture-localhost-5173-submit-2025-10-04-22_31_14" src="https://github.com/user-attachments/assets/5ee09822-4310-47f2-86a9-96d7a0a27e3e" />

<img width="3456" height="2476" alt="screencapture-localhost-5173-dashboard-2025-10-05-14_37_27" src="https://github.com/user-attachments/assets/8f6d19f7-0d92-4b4b-ada5-87fbf3a52cab" />

<img width="3456" height="2964" alt="screencapture-localhost-5173-startups-19ff177d-e50b-49de-8bec-083b429917dd-2025-10-05-14_38_00" src="https://github.com/user-attachments/assets/20be7b22-cf54-4688-ae21-52101b6ffe85" />

<img width="3456" height="9256" alt="screencapture-localhost-5173-startups-19ff177d-e50b-49de-8bec-083b429917dd-analysis-2025-10-05-14_38_26" src="https://github.com/user-attachments/assets/e98ffaa5-b465-4abc-b92f-3992c5a9fe37" />

## 🧠 Core AI Engine

The backend is powered by a multi-agent system designed to mimic an expert analyst team:

### Orchestrator Agent
- "Manager" agent that receives startup submissions
- Delegates tasks to specialist agents
- Coordinates workflow and ensures completeness

### Specialist Agents
Each agent has a distinct role and is equipped with tools like web search:

- **Team Agent**: Evaluates founder-market fit, experience, and team completeness
- **Market Agent**: Analyzes and validates market size (TAM/SAM/SOM) and trends
- **Product & Traction Agent**: Assesses product value proposition and key performance metrics
- **Competition Agent**: Identifies competitive landscape and defensible moat
- **Synthesis Agent**: Compiles specialist reports into cohesive investment memo

## 🎯 Key Frontend Features for Investors

### 1. Interactive Investment Dashboard
- Standardized view for easy startup comparison
- At-a-glance summary with "Investability Score"
- Critical risks and opportunities identification
- Scored analysis cards (1-10 scale) with data visualizations

### 2. AI Transparency & Traceability
- "Agent Trace" Log showing step-by-step reasoning
- Clickable source citations for every data point
- Direct links to original documents and sources
- Full audit trail of AI decision-making process

### 3. Conversational Co-pilot
- Chat interface for deep Q&A with the analysis
- Human-in-the-loop feedback capability
- Real-time dashboard updates based on feedback
- Dynamic re-analysis triggers

### 4. Collaboration & Deal Flow Management
- Status tracking (Shortlisted, Rejected, Watching)
- Team notes and shared comments
- Centralized record of team thoughts and decisions

## 🛠️ Technologies Used

### Backend
- **Google ADK (Agent Development Kit)**: Core framework for multi-agent system
- **FastAPI**: High-performance web framework
- **Google Gemini**: AI models for analysis and reasoning
- **BigQuery**: Data storage and analytics
- **Pydantic**: Data validation and serialization

### Frontend
- **React 19 + TypeScript**: Interactive user interface
- **Tailwind CSS 4**: Modern styling framework
- **Shadcn UI**: Beautiful, accessible components
- **LangGraph SDK**: Agent communication
- **React Router**: Navigation and routing

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js**
- **uv** (Python package manager)
- **Google Cloud Project** with Vertex AI API enabled
- **BigQuery** dataset setup

### Installation

1. **Clone and Navigate**
   ```bash
   cd a:\project\adk-samples\python\agents\Project-Younicorn
   ```

2. **Install Dependencies**
   ```bash
   make install
   ```

3. **Set Environment Variables**
   ```bash
   # Create .env file in app/ directory
   echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> app/.env
   echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> app/.env
   echo "BIGQUERY_DATASET=Younicorn_dataset" >> app/.env
   ```

4. **Run Development Servers**
   ```bash
   make dev
   ```

Your platform will be running at `http://localhost:5173`.

## 📁 Project Structure

```
Project-Younicorn/
├── app/                    # Backend application
│   ├── agents/            # Specialist AI agents
│   ├── models/            # Data models and schemas
│   ├── services/          # Business logic services
│   ├── storage/           # BigQuery integration
│   └── config.py          # Configuration settings
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API communication
│   │   └── types/         # TypeScript definitions
└── docs/                  # Documentation
```

## 🔧 Development

- **Backend Development**: `make dev-backend`
- **Frontend Development**: `make dev-frontend`
- **Run Tests**: `make test`
- **Lint Code**: `make lint`

## 📊 Data Storage

Project Younicorn uses BigQuery for:
- Startup submission data
- Analysis results and metrics
- User collaboration data
- Agent trace logs
- Source citations and references

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.

