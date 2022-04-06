# BUILT-INS
from os import getenv
import json
from datetime import datetime as dt

# VENDOR
import aiofiles
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import FileResponse

# SOURCE
from src.spiders import WordSpider

if getenv("OH_ENV") == "production":
    settings = dict(
        domain="dadescomunals.tk",
        port=8000,
        baseurl="/openhemeroteca/",
        storage="/tmp",
    )
else:
    settings = dict(domain="localhost", port=8000, baseurl=None, storage="tmp")

app = FastAPI()

origins = ["http://localhost:9000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/public", StaticFiles(directory="src/server/static"), name="static")

spider = WordSpider(settings)


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
