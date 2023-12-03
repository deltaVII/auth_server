from fastapi import FastAPI

from .auth.router import router as auth_router
from .tests.test_auth import  router as test_auth_router
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