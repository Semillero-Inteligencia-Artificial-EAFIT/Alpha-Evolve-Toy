from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
from tools.tools import CodeOptimizer

app = FastAPI()
templates = Jinja2Templates(directory="templates")

optimizer = CodeOptimizer()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/optimize")
async def optimize_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    iterations = data.get("iterations", 5)
    runs = data.get("runs", 3)
    use_claude = data.get("use_claude", False)
    api_key = data.get("api_key", "")
    
    result = await optimizer.optimize(code, iterations, runs, use_claude, api_key)
    return result

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    return optimizer.get_task_status(task_id)