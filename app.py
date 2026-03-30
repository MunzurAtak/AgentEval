import threading
import time
import uvicorn
import os
from app.main import app as fastapi_app
from app.storage.database import init_db
import gradio_app

# Initialise database
init_db()

# Start FastAPI in a background thread
def start_api():
    uvicorn.run(fastapi_app, host='0.0.0.0', port=8000, log_level='warning')

api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()

# Give the API a moment to start before Gradio tries to connect
time.sleep(2)

# Point Gradio at the local API
os.environ['API_BASE'] = 'http://localhost:8000/api/v1'

# Launch Gradio (this blocks and serves the UI)
gradio_app.demo.launch(server_name='0.0.0.0', server_port=7860)
