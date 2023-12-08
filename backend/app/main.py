from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.router import router as auth_router
from .tests.test_auth import  router as test_auth_router
from .database import get_async_session
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello world"}


app.include_router(
    auth_router
)
app.include_router(
    test_auth_router
)