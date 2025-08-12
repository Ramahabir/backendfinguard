from fastapi import FastAPI, Request
from analyze import app
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class RequestModel(BaseModel):
    message: str
    language: str

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/get")
def get_request():
    return {"message": "GET request successful"}


@api.post("/analyze")
async def analyze(request: RequestModel):
    result = app.invoke({
        "messages": request.message,
        "language": request.language
    })
    return result