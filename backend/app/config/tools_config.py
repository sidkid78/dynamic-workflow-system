# app/config/tools_config.py
"""
Configuration for tools used by the autonomous agent
"""

# Tool setup info
TOOL_CONFIG = {
    "web_search": {
        "enabled": True,
        "max_results_per_query": 5,
        "rate_limit": {
            "max_queries_per_minute": 10,
            "max_queries_per_hour": 100
        }
    },
    "calculator": {
        "enabled": True,
        "allowed_functions": ["add", "subtract", "multiply", "divide", "sqrt", "pow"]
    },
    "wikipedia": {
        "enabled": True,
        "max_summary_length": 1000
    }
}

# Environment variable configuration examples for documentation
ENVIRONMENT_VARIABLES = """
# Google Custom Search Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id

# Example .env file format
# Add these variables to your .env file
GOOGLE_API_KEY=AIza...
GOOGLE_CSE_ID=123456...
"""

# Rate limiting helpers
class RateLimiter:
    def __init__(self, max_per_minute=10, max_per_hour=100):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.minute_usage = 0
        self.hour_usage = 0
        self.last_minute_reset = 0
        self.last_hour_reset = 0
        
    def check_rate_limit(self):
        """Check if rate limit is exceeded"""
        import time
        
        current_time = time.time()
        
        # Reset minute counter if a minute has passed
        if current_time - self.last_minute_reset > 60:
            self.minute_usage = 0
            self.last_minute_reset = current_time
        
        # Reset hour counter if an hour has passed
        if current_time - self.last_hour_reset > 3600:
            self.hour_usage = 0
            self.last_hour_reset = current_time
        
        # Check if either limit is exceeded
        if self.minute_usage >= self.max_per_minute:
            return False, "Minute rate limit exceeded"
        
        if self.hour_usage >= self.max_per_hour:
            return False, "Hour rate limit exceeded"
        
        # Increment counters
        self.minute_usage += 1
        self.hour_usage += 1
        
        return True, "Rate limit check passed"