
import asyncio
from agentic_sdlc.orchestration.api_model_management.database import initialize_database

try:
    asyncio.run(initialize_database("test.db"))
    print("Success")
except ValueError as e:
    print(f"ValueError: {e}")
except Exception as e:
    print(f"Error: {e}")
