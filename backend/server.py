from typing import Optional
import uuid
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from memory import Memory
import boto3
from context import prompt

load_dotenv(override=True)

app = FastAPI()

system_prompt = ""

USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")

# Initialize S3 client if needed
if USE_S3:
    s3_client = boto3.client("s3")

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def load_system_prompt():
    with open("me.txt", "r") as f:
        system_prompt = f.read()
        print("System Prompt Loaded", system_prompt)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


load_system_prompt()

@app.get("/")
async def root():
    return {
        "message": "Who Am AI API",
        "memory_enabled": True,
        "storage": "S3" if USE_S3 else "local",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "use_s3": USE_S3}

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    try:
    
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        session_id = request.session_id or str(uuid.uuid4())
        memory = Memory()
        history_messages = memory.load_conversation(session_id, prompt())
        history_messages.append({"role":"user", "content": request.message})
        print("Loaded Conversations", history_messages)

        response_content = get_response_from_openai(client, history_messages)
        history_messages.append({"role":"assistant", "content": response_content})
        print("Updated Conversations", history_messages)
        memory.save_conversation(session_id, history_messages)
        return ChatResponse(response=response_content, session_id=session_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def get_response_from_openai(client, history_messages):
    response = client.chat.completions.create(  
        model="gpt-4o-mini",    
        messages=history_messages
    )
    return response.choices[0].message.content

