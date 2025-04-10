from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import os

app = FastAPI()

BASE_PROMPT = """
You are BayportBot, a helpful and friendly AI assistant for Bayport Botswana. You help users with:
- Downloading statements 📑
- Booking settlements 📅
- Requesting a callback 📞
- Understanding loan products and services
- Performing loan calculations
You must respond concisely and accurately, guiding users step-by-step.
"""

class UserQuery(BaseModel):
    message: str
    user_id: Optional[str] = None

async def query_openai(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', 'your_openai_key')}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": BASE_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            },
            headers=headers
        )
    result = response.json()
    return result["choices"][0]["message"]["content"]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bayport AI Agent</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 2rem;
            }
            .container {
                background: white;
                padding: 2rem;
                border-radius: 10px;
                max-width: 600px;
                margin: auto;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1b365d;
            }
            ul {
                list-style: none;
                padding-left: 0;
            }
            ul li {
                margin: 0.5rem 0;
                padding-left: 1rem;
                position: relative;
            }
            ul li::before {
                content: \"✔\";
                color: #1b365d;
                position: absolute;
                left: 0;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Bayport AI Agent</h1>
            <p>This digital assistant can help you:</p>
            <ul>
                <li>Download financial statements</li>
                <li>Book settlements</li>
                <li>Request callbacks</li>
                <li>Chat with our AI agent</li>
            </ul>
            <p>👉 <a href='/docs'>Click here to open the full API interface</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_with_user(user_query: UserQuery):
    user_message = user_query.message
    response = await query_openai(user_message)
    return {"response": response}

@app.get("/download-statement")
async def download_statement(user_id: str):
    return {"message": f"Statement for user {user_id} downloaded successfully."}

@app.post("/book-settlement")
async def book_settlement(data: dict):
    return {"message": "Settlement successfully booked.", "details": data}

@app.post("/request-callback")
async def request_callback(data: dict):
    return {"message": "Callback request received.", "details": data}
