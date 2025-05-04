import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from app.models.schemas import WorkflowResponse, AgentResponse

class ResponseSaver:
    def __init__(self, base_dir: str = "responses"):
        """
        Initialize the ResponseSaver with a base directory for saving responses.
        
        Args:
            base_dir (str): Base directory where responses will be saved. Defaults to "responses".
        """
        self.base_dir = Path(base_dir)
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create the base directory if it doesn't exist."""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _format_filename(self, session_id: str, timestamp: Optional[datetime] = None) -> str:
        """
        Generate a filename for the response.
        
        Args:
            session_id (str): The session ID from the workflow response.
            timestamp (datetime, optional): Timestamp to use in filename. Defaults to current time.
        
        Returns:
            str: Formatted filename
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        formatted_time = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"response_{formatted_time}_{session_id}.md"
    
    def _format_markdown(self, response: WorkflowResponse) -> str:
        """
        Format the workflow response as a markdown document.
        
        Args:
            response (WorkflowResponse): The workflow response to format.
        
        Returns:
            str: Formatted markdown content
        """
        lines = [
            f"# Agent Response - {response.selected_workflow}",
            "",
            f"**Session ID**: {response.session_id}",
            f"**Processing Time**: {response.processing_time:.2f} seconds",
            "",
            "## Final Response",
            "",
            response.final_response,
            "",
        ]
        
        if response.intermediate_steps:
            lines.extend([
                "## Intermediate Steps",
                ""
            ])
            
            for step in response.intermediate_steps:
                lines.extend([
                    f"### {step.agent_role}",
                    "",
                    step.content,
                    "",
                    "**Metadata:**",
                    "```json",
                    json.dumps(step.metadata, indent=2) if step.metadata else "{}",
                    "```",
                    ""
                ])
        
        if response.error:
            lines.extend([
                "## Errors",
                "",
                f"```\n{response.error}\n```",
                ""
            ])
        
        return "\n".join(lines)
    
    def save_response(self, response: WorkflowResponse) -> Path:
        """
        Save a workflow response to a markdown file.
        
        Args:
            response (WorkflowResponse): The workflow response to save.
        
        Returns:
            Path: Path to the saved file.
        """
        filename = self._format_filename(response.session_id)
        file_path = self.base_dir / filename
        
        markdown_content = self._format_markdown(response)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return file_path 