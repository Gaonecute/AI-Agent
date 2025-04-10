from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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
            form {
                margin-bottom: 1rem;
            }
            input, textarea, button {
                width: 100%;
                padding: 0.5rem;
                margin-top: 0.5rem;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            button {
                background-color: #1b365d;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #16294d;
            }
            a {
                color: #007bff;
                text-decoration: none;
                display: block;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Bayport AI Agent</h1>

            <h3>💬 Chat with AI Agent</h3>
            <form action="/chat-ui" method="post">
                <input type="text" name="message" placeholder="Type your question..." required>
                <button type="submit">Ask AI</button>
            </form>

            <h3>📞 Request a Callback</h3>
            <form action="/request-callback-ui" method="post">
                <input type="text" name="name" placeholder="Your Name" required>
                <input type="text" name="phone" placeholder="Phone Number" required>
                <button type="submit">Request Callback</button>
            </form>

            <h3>📅 Book a Settlement</h3>
            <form action="/book-settlement-ui" method="post">
                <input type="text" name="account" placeholder="Account Number" required>
                <input type="text" name="date" placeholder="Preferred Date" required>
                <button type="submit">Book Settlement</button>
            </form>

            <a href="/docs">🛠️ Open Developer API Interface (Swagger)</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat-ui")
async def chat_ui(message: str = Form(...)):
    response = await query_openai(message)
    return HTMLResponse(f"<h2>AI Response:</h2><p>{response}</p><a href='/'>🔙 Go Back</a>")

@app.post("/request-callback-ui")
async def request_callback_ui(name: str = Form(...), phone: str = Form(...)):
    data = {"name": name, "phone": phone}
    return HTMLResponse(f"<h2>Callback Requested</h2><p>Name: {name}<br>Phone: {phone}</p><a href='/'>🔙 Go Back</a>")

@app.post("/book-settlement-ui")
async def book_settlement_ui(account: str = Form(...), date: str = Form(...)):
    data = {"account": account, "date": date}
    return HTMLResponse(f"<h2>Settlement Booked</h2><p>Account: {account}<br>Date: {date}</p><a href='/'>🔙 Go Back</a>")

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
