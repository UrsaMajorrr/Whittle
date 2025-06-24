import uvicorn
from pathlib import Path
import os

def main():
    # Change to the project root directory
    os.chdir(Path(__file__).parent.parent.parent.parent)
    
    # Run the server
    uvicorn.run(
        "whittle.src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # Enable auto-reload during development
    )

if __name__ == "__main__":
    main() 