from mcp.server.fastmcp import FastMCP, Context 
from app.services.file_system import FileSystemService 
from app.services.tool_service import ToolService 

mcp = FastMCP("Build5Tools", dependencies=["fastapi", "uvicorn"])

file_system = FileSystemService()
rag_tools = ToolService()

@mcp.resource("knowledge//query")
def knowledge_query_description() -> str:
    """Description resource for knowledge base queries"""
    return "Use this resource to search the knowledge base. Access with knowledge://query?q={search_term}"

@mcp.resource("knowledge://query", params=["q"])
def query_knowledge(q: str) -> str:
    """Search the knowledge base for relevant information"""
    results = rag_tools.retrieve(q, top_k=5)
    formatted_results = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(results)])
    return formatted_results