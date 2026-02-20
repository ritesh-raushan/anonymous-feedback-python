from fastapi import FastAPI
from .models import model
from .database import engine
from .routers import auth

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def root():
    return "Hello World"