import logging
from typing import List, Dict, Any
from app.services.rag_tools import RAGRetrieverTool
# from app.services.file_system import FileSystemService # Don't import directly
from app.dependencies import get_file_system_service # Import the getter
# from app.core.workflows.autonomous_agent import ToolDefinition # Old import
from app.models.schemas import ToolDefinition # Import from schemas

logger = logging.getLogger(__name__)

class RAGRetrieverWrapper:
    """Wraps the RAGRetrieverTool to provide tool definitions for the registry."""

    def __init__(self):
        try:
            # Ideally get FileSystemService via dependency injection
            # self.fs_service = FileSystemService() # Don't instantiate directly
            self.fs_service = get_file_system_service() # Use the dependency getter
            # Consider making the embedding model configurable (e.g., via env var)
            self.retriever = RAGRetrieverTool(
                file_system_service=self.fs_service,
                embedding_model="gemini-embedding-exp-03-07" # Default or configured model
            )
            self.is_setup = True
            logger.info("RAGRetrieverWrapper initialized with RAGRetrieverTool.")
        except Exception as e:
            logger.error(f"Failed to initialize RAGRetrieverWrapper: {e}", exc_info=True)
            self.retriever = None
            self.is_setup = False

    def get_function_definition(self) -> List[ToolDefinition]:
        """Returns a list of ToolDefinition objects for the retriever's capabilities."""
        if not self.is_setup or not self.retriever:
            return []

        definitions = [
            ToolDefinition(
                name="rag_search_workspace",
                description="Searches the agent's workspace (previously scraped/saved documents) for information relevant to a query. Can use keyword or semantic search.",
                parameters={
                    "workspace_id": {"type": "string", "description": "The ID of the agent's workspace (usually the agent_id).", "required": True},
                    "query": {"type": "string", "description": "The search query.", "required": True},
                    "use_semantic": {"type": "boolean", "description": "Whether to use semantic search (True) or keyword search (False). Defaults to True if embeddings available.", "required": False},
                    "max_results": {"type": "integer", "description": "Maximum number of search results to return (default: 5).", "required": False}
                },
                # Assuming retriever.search is awaitable or handled correctly by execution flow
                function=self.retriever.search
            )
            # Note: format_results_as_context is more of a utility, not typically exposed as a direct agent tool.
            # The agent should receive the structured results from 'search' and use its LLM capabilities
            # to synthesize the information or use it in subsequent steps.
        ]
        return definitions

# Optional execute method if direct execution is needed
# async def execute_search(self, workspace_id: str, query: str, use_semantic: bool = True, max_results: int = 5):
#     if not self.is_setup: return {"status": "error", "message": "RAG retriever not initialized."}
#     # Assuming search is awaitable or handled correctly.
#     # The underlying RAGRetrieverTool.search seems synchronous based on rag_tools.py
#     # Need to ensure async compatibility if called with await.
#     return self.retriever.search(workspace_id, query, use_semantic, max_results) 