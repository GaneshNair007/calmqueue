"""CalmQueue Launch Script."""

import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    backend_dir = root / "backend"
    sys.path.insert(0, str(backend_dir))

    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)

    print("=================================================================")
    print("   CALMQUEUE - Open-Source AI Notification Priority Engine      ")
    print("   Hacktoberfest 2026 Week 3 Challenge: Slow and Steady         ")
    print("=================================================================")
    print("   Dashboard URL: http://localhost:8000                          ")
    print("   Swagger Docs:  http://localhost:8000/docs                     ")
    print("   Press Ctrl+C to stop the server.                              ")
    print("=================================================================")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, app_dir=str(backend_dir))

if __name__ == "__main__":
    main()
