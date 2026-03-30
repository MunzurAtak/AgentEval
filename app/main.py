from fastapi import FastAPI
from app.api.routes import router
from app.storage.database import init_db

app = FastAPI(
    title='AgentEval',
    description='Automated LLM debate evaluation pipeline',
    version='1.0.0',
)


@app.on_event('startup')
def startup():
    """Initialise the database when the server starts."""
    init_db()


# Register all routes under /api/v1
app.include_router(router, prefix='/api/v1')
