from fastapi import FastAPI
from .models import model
from .database import engine

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return "Hello World"