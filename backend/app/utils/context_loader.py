import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def load_context_content(file_path: Optional[str]) -> str:
    """
    Safely loads content from the specified context file.

    Args:
        file_path: The absolute path to the context file.

    Returns:
        The content of the file as a string, or an empty string if 
        the path is None, the file doesn't exist, or an error occurs.
    """
    if not file_path:
        logger.info("No context file path provided.")
        return ""
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.warning(f"Context file not found or is not a file: {file_path}")
        # You might want to raise an error here if context is mandatory
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Successfully loaded context from: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading context file {file_path}: {e}", exc_info=True)
        return "" # Return empty string on error to avoid breaking prompts 