from fastapi import FastAPI

from app.api.routes.query import router as query_router


app = FastAPI(
    title="Telarc",
    description="Telecom Knowledge Assistant",
    version="1.0.0",
)


app.include_router(query_router)