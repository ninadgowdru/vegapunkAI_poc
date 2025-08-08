from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
from ai_poc import generate_poc

app = FastAPI(title="VegapunkAI PoC Generator")

# Serve static frontend
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

class PoCRequest(BaseModel):
    vuln_description: str
    target: str
    language: str = "python"

@app.post("/api/generate_poc")
async def api_generate_poc(req: PoCRequest):
    result = generate_poc(req.vuln_description, req.target, req.language)
    return JSONResponse(content=result)

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("../frontend/index.html")

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
