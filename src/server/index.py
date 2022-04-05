# BUILT-INS
import json
from datetime import datetime as dt

# VENDOR
import aiofiles
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import FileResponse

# SOURCE
from src.spiders import WordSpider

app = FastAPI()

app.mount("/public", StaticFiles(directory="src/server/static"), name="static")

spider = WordSpider()


@app.get("/")
async def index() -> HTMLResponse:
    async with aiofiles.open("src/server/static/index.html") as fconn:
        return HTMLResponse(await fconn.read())


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    data = json.loads(await ws.receive_text())

    if data.get("type") == "query":
        await spider.crawl(ws, data["word"], data["start_date"], data["end_date"])
    else:
        await ws.send_text(
            json.dumps({"type": "error", "body": {"message": "Que vosss?"}})
        )


@app.get("/file/{id}")
async def file(id: str) -> FileResponse:
    return FileResponse("tmp/%s.csv" % id)
