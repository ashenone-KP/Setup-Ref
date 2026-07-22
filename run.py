"""Development entry point: `python run.py`."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    # Reloader disabled so the server runs as a single process.
    app.run(debug=debug, port=port, use_reloader=False)
