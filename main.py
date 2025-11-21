from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

# Import Agents
from agent1.Agent1Runner import Agent1Runner
from agent2.Agent2Runner import Agent2Runner

app = FastAPI(title="Banking AI Agents System")

# Initialize Runners
agent1_runner = Agent1Runner()
agent2_runner = Agent2Runner()

@app.get("/")
def read_root():
    return {"message": "Banking AI System is running. Use /docs to test endpoints."}

# --- Agent 1 Endpoint ---
@app.post("/agent1/categorize")
async def run_agent_1(
    file1: UploadFile = File(..., description="File1.csv: Domains and Owners"),
    file2: UploadFile = File(..., description="File2.csv: Banking Elements")
):
    """
    Agent 1: Takes two CSVs, maps elements to domains using Gemini AI.
    Returns JSON and Markdown.
    """
    try:
        content1 = await file1.read()
        content2 = await file2.read()
        
        result = agent1_runner.run(content1, content2)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Agent 2 Endpoint ---
class Agent2Request(BaseModel):
    categorized_data: Dict[str, Any] # The JSON output from Agent 1
    owner_name: str

@app.post("/agent2/generate-er")
async def run_agent_2(request: Agent2Request):
    """
    Agent 2: Takes the JSON from Agent 1 and an Owner Name.
    Returns Mermaid Code and System JSON.
    """
    try:
        result = agent2_runner.run(request.categorized_data, request.owner_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)