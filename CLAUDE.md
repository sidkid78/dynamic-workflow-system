# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dynamic Workflow System - An intelligent multi-agent platform that automatically selects and executes optimal workflow patterns based on user queries. The system uses Google Gemini LLM with function calling to analyze queries and route them through six distinct workflow patterns, each optimized for different task types.

**Tech Stack:**
- Backend: FastAPI + Python 3.12+ (async/await)
- Frontend: Next.js 15.3 + React 19 + TypeScript
- LLM: Google Gemini 2.5 Pro (Developer API or Vertex AI)
- Styling: Tailwind CSS 4.1.3 with Radix UI components

## Development Commands

### Starting the Application

**Full stack (PowerShell on Windows):**
```powershell
.\start-servers.ps1
```
This launches both backend (port 8000) and frontend (port 3000) in separate windows.

**Backend only:**
```bash
cd backend
# Activate venv (Windows)
venv\Scripts\activate.ps1
# Or on Linux/Mac
source venv/bin/activate

# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend only:**
```bash
cd frontend
npm run dev    # Development server on port 3000
npm run build  # Production build
npm start      # Production server
npm run lint   # ESLint checking
```

### Testing & Development

**Backend:**
- No test suite currently implemented
- Use `/health` endpoint to verify tool configuration
- Check logs for tool initialization status on startup

**Frontend:**
- `/test-workflow` page for workflow testing
- `/debug` page for debugging interface
- Browser console for React dev tools

## Architecture Overview

### Core Workflow Selection System

The system uses **LLM-based dynamic routing** to select the optimal workflow pattern:

1. User submits query → POST `/api/workflows/process`
2. `workflow_selector.py` uses Gemini function calling to analyze query
3. Returns one of 6 workflow patterns + appropriate agent personas
4. Selected workflow executes with intermediate steps captured
5. Response includes final answer, all agent contributions, and metrics

### Six Workflow Patterns

Each pattern optimized for specific query types:

1. **prompt_chaining** - Sequential 3-stage pipeline (Processor → Validator → Refiner)
   - Use for: Linear tasks building on previous steps

2. **routing** - Classifier routes to specialized handlers
   - Use for: Categorized inquiries (Technical/Account/General)

3. **parallel_sectioning** - Divides task into independent parallel components
   - Use for: Multi-perspective analysis (marketing + technical + financial)

4. **parallel_voting** - Executes same task multiple times, builds consensus
   - Use for: High-confidence decisions (moderation, security assessment)

5. **orchestrator_workers** - Central orchestrator breaks into subtasks, workers execute with dependency management
   - Use for: Complex multi-faceted queries (vacation planning, codebase refactoring)
   - **Most complex workflow**: 3 phases (Planning → Execution → Synthesis)

6. **evaluator_optimizer** - Iterative generation and refinement cycle
   - Use for: Content refinement (emails, poetry, SQL optimization)

7. **Autonomous Agent** (special mode via `use_autonomous_exclusively` flag)
   - Self-directed planning and execution loop with tool access
   - Plans → Acts → Reflects iteratively

### Agent Personas System

Located in `backend/app/personas/agent_personas.py`:
- Each workflow has specialized agents with role, persona, description, strengths
- Example: `orchestrator_workers` has orchestrator_agent, worker_agent, synthesizer_agent
- Personas loaded dynamically based on selected workflow

### Tool System Architecture

**Registry Pattern** (`backend/app/tools/registry.py`):
- Global singleton `_global_tools` dictionary
- Tools auto-register on import via `register_tool(tool_definition)`
- Tool definitions include: name, description, JSON schema parameters, callable function

**Available Tools:**
- Calculator (`calculator.py`)
- Web Search (`web_search.py`) - requires GOOGLE_API_KEY + GOOGLE_CSE_ID
- File System operations (`file_system_tools.py`)
- Git operations (`git_tools.py`)
- Code execution (`code_execution_tools.py`)
- Batch operations (`batch_tools.py`)
- Web scraping (`web_scraper_wrapper.py`)
- RAG retrieval (`rag_retriever_wrapper.py`)

**Tool Initialization:**
- Happens on FastAPI startup via `@app.on_event("startup")`
- Tools imported in `main.py:init_tools()`
- Check `/health` endpoint for tool configuration status

### LLM Client Architecture

Two client classes in `backend/app/core/llm_client.py`:

1. **GoogleGeminiClient** (Singleton)
   - Basic text generation
   - Supports async/sync/streaming modes
   - Auto-continuation for truncated responses
   - Configurable thinking budget for advanced reasoning
   - Handles both Developer API and Vertex AI

2. **GoogleGeminiFunctions** (Singleton)
   - Function calling capabilities
   - Used by workflow_selector for dynamic workflow choice
   - Structured function invocation

**Configuration:**
- Set `GOOGLE_API_KEY` + `GEMINI_MODEL` for Developer API
- Or set `USE_VERTEX_AI=true` + `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION` for Vertex
- Optional: `GEMINI_THINKING_BUDGET=-1` for advanced reasoning

### Backend Structure

```
backend/app/
├── main.py                    # FastAPI app, CORS, startup/health endpoints
├── config.py                  # Pydantic BaseSettings config from .env
├── models/schemas.py          # Request/Response Pydantic models
├── api/endpoints/workflows.py # Main workflow processing endpoint
├── core/
│   ├── llm_client.py          # Gemini client (basic + functions)
│   ├── workflow_selector.py   # LLM-based workflow selection
│   └── workflows/             # 6 workflow pattern implementations
├── personas/agent_personas.py # Agent role definitions
├── tools/
│   ├── registry.py            # Global tool registration system
│   ├── base.py                # Base Tool class
│   └── [tool modules]         # Individual tool implementations
├── services/
│   ├── rag_tools.py           # RAG implementation
│   └── tool_service.py        # Tool orchestration
└── utils/
    ├── response_saver.py      # Persistence for responses
    └── context_loader.py      # External context file loading
```

### Frontend Structure

```
frontend/src/
├── app/                       # Next.js app router
│   ├── page.tsx              # Landing page
│   ├── chat/page.tsx         # Main chat interface
│   ├── test-workflow/page.tsx # Workflow testing
│   └── debug/page.tsx        # Debug interface
├── components/
│   ├── ui/                   # Reusable primitives (button, card, alert, etc.)
│   ├── chat/                 # Message list, input, enhanced rendering
│   └── workflow/             # Agent cards, metrics, diagrams
├── hooks/use-chat.ts         # Chat state management + localStorage persistence
├── lib/
│   ├── api.ts                # API client functions
│   └── utils.ts              # Utility functions
└── types/index.ts            # TypeScript interfaces
```

### Data Flow: User Query to Response

```
User Input
    ↓
Frontend: use-chat.ts hook captures query
    ↓
POST /api/workflows/process with QueryRequest
    ↓
Backend: select_workflow() analyzes via Gemini function calling
    ↓
Route to selected workflow pattern (e.g., orchestrator_workers)
    ↓
Execute workflow with agent personas + tool registry
    ↓
Collect intermediate_steps (all agent responses)
    ↓
Return WorkflowResponse with final_response + steps + metrics
    ↓
Frontend: Render in chat + visualize workflow diagram
    ↓
LocalStorage: Persist session (up to 50 messages)
```

### Session Management

**Frontend (`use-chat.ts`):**
- Session ID persisted in localStorage
- Message history maintained (max 50 messages)
- Auto-loads previous session on page refresh
- Graceful handling of storage quota exceeded

**Backend:**
- Session ID returned in WorkflowResponse
- Optional user_id for multi-user scenarios
- Responses optionally saved to `/responses` directory if `SAVE_RESPONSES=true`

## Configuration & Environment

### Required Environment Variables

Copy `backend/env.example` to `backend/.env` and configure:

```bash
# Core Settings
DEBUG=true
APP_NAME="Dynamic Workflow System"
APP_VERSION="0.1.0"

# LLM Configuration (REQUIRED - choose one approach)
# Option 1: Gemini Developer API (simplest)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-pro

# Option 2: Vertex AI (enterprise)
# USE_VERTEX_AI=true
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_CLOUD_LOCATION=us-central1

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Workflow Settings
DEFAULT_WORKFLOW=orchestrator_workers
MAX_RETRIES=3
TIMEOUT_SECONDS=120

# Storage Settings
SAVE_RESPONSES=true
CONTEXT_FILE_PATH=./context.md
```

### Optional: Web Search Tool

To enable web search tool:
```bash
GOOGLE_API_KEY=your_google_api_key  # Can reuse LLM key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

### Directory Creation on Startup

Backend automatically creates:
- `agent_workspace/` - Runtime workspace for agent operations
- `responses/` - Persistent storage for workflow responses (if `SAVE_RESPONSES=true`)
- `run_outputs/` - Output storage for batch operations

## Key Implementation Details

### Orchestrator-Workers Workflow (Most Complex)

**Phase 1: Task Planning**
- Orchestrator LLM analyzes query
- Returns structured plan: subtasks + dependencies + priorities

**Phase 2: Subtask Execution**
- Worker agents execute in parallel when dependencies met
- Respects priority ordering
- Supports context injection from external files

**Phase 3: Result Synthesis**
- Synthesizer integrates worker outputs
- Creates unified cohesive response
- Validates outputs don't verbatim copy worker results

### Migration Notes

- **Recently migrated from Azure OpenAI to Google Gemini**
- Legacy Azure settings commented in `config.py` for reference
- Context file loading infrastructure exists but currently deactivated
- Tool system refactored from basic to registry-based pattern

### Error Handling

**Frontend:**
- Network error detection in API calls
- Error boundary components for React errors
- Graceful degradation when localStorage unavailable

**Backend:**
- Try-catch with fallback to default workflow on selection failure
- HTTP 500 responses with error details
- Tool initialization errors logged but don't prevent startup
- Individual workflow errors captured in intermediate_steps

### CORS Configuration

Default CORS origins: `localhost:3000-3004`
- Configure via `CORS_ORIGINS` in `.env`
- Format: JSON array of strings

## Working with This Codebase

### Adding a New Workflow Pattern

1. Create workflow file in `backend/app/core/workflows/`
2. Define workflow execution function
3. Add agent personas to `personas/agent_personas.py`
4. Register in workflow selector's available workflows
5. Update frontend workflow visualization if needed

### Adding a New Tool

1. Create tool file in `backend/app/tools/`
2. Define tool class or function
3. Create `ToolDefinition` with JSON schema parameters
4. Call `register_tool()` to add to global registry
5. Import in `main.py:init_tools()` for auto-registration
6. Test via `/api/workflows/tools` endpoint

### Modifying Agent Personas

Edit `backend/app/personas/agent_personas.py`:
- Each workflow has its own persona dictionary
- Fields: role, persona, description, strengths
- Used for LLM system prompts in workflow execution

### Frontend API Integration

All API calls go through `frontend/src/lib/api.ts`:
- Base URL: `process.env.NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api`)
- Main endpoint: `processWorkflow(query, sessionId)`
- Returns typed `WorkflowResponse` interface from `types/index.ts`

### Debugging Tips

1. **Backend logs**: Check terminal for tool initialization, workflow selection, LLM calls
2. **Frontend DevTools**: React components, state in `use-chat` hook, localStorage inspection
3. **Health endpoint**: `GET /health` shows tool configuration status
4. **Test pages**: Use `/test-workflow` or `/debug` for isolated testing
5. **Intermediate steps**: All agent contributions visible in response for transparency

## Important Caveats

- No test suite currently implemented (backend or frontend)
- Web search tool requires separate Google Custom Search Engine setup
- Context file loading (`CONTEXT_FILE_PATH`) infrastructure exists but not actively used
- Session persistence uses localStorage (browser-specific, 5-10MB limit)
- LLM thinking budget (`GEMINI_THINKING_BUDGET`) only works with Gemini 2.5 Pro models
- Autonomous agent mode not exposed in default UI (requires `use_autonomous_exclusively` flag)
