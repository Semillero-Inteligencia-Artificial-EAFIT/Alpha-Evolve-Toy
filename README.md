# Code Optimizer

AI-powered Python code optimization with real-time performance metrics visualization.

## Features

- Optimize Python code using OpenAI or Claude Code API
- Real-time performance tracking (CPU, Memory, Execution Time)
- Interactive charts showing optimization progress
- Iterative improvement algorithm
- Web-based interface

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Start the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access the web interface at: http://localhost:8000

## How It Works

1. Input your Python code
2. Select LLM provider (OpenAI or Claude)
3. Enter your API key
4. Set optimization parameters (iterations, runs per test)
5. Click "Optimize Code"
6. Watch real-time metrics and charts
7. Get the optimized code with performance improvements

## Configuration

- **Iterations**: Maximum optimization cycles (default: 5)
- **Runs per test**: Number of executions for averaging metrics (default: 3)
- **LLM Provider**: Choose between OpenAI or Claude Code API
- **API Key**: Required for both providers

## API Endpoints

- `GET /` - Web interface
- `POST /optimize` - Start optimization
- `GET /status/{task_id}` - Check optimization status

## File Structure

```
├── main.py              # FastAPI application
├── tools/
│   ├── __init__.py      # Package initialization
│   └── tools.py         # Core optimization engine
├── templates/
│   └── index.html       # Web UI
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```