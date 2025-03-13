# Project structure

dynamic-workflow-system/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── models/                # Pydantic models for request/response validation
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   └── workflows.py
│   │   └── dependencies.py
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── llm_client.py      # LLM API client
│   │   ├── workflow_selector.py
│   │   └── workflows/
│   │       ├── __init__.py
│   │       ├── prompt_chaining.py
│   │       ├── routing.py
│   │       ├── parallel_sectioning.py
│   │       ├── parallel_voting.py
│   │       ├── orchestrator_workers.py
│   │       └── evaluator_optimizer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py
│   └── personas/
│       ├── __init__.py
│       └── agent_personas.py
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

