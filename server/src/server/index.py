# BUILT-INS
from os import getenv, path
import json
from datetime import datetime as dt
import sys
import traceback

# VENDOR
import aiofiles
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# SOURCE
from src.spiders import WordSpider

if getenv("OH_ENV") == "production":
    settings = dict(
        domain="dadescomunals.org",
        port=8000,
        baseurl="/hemeroteca-oberta/",
        storage="/tmp",
    )
else:
    settings = dict(
        domain="localhost", port=8000, baseurl=None, storage=path.join("..", "storage")
    )

app = FastAPI()

origins = [
    "http://dadescomunals.org",
    "https://dadescomunals.org",
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/server/static"), name="static")

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
        try:
            await spider.crawl(ws, data["word"], data["start_date"], data["end_date"])
        except WebSocketDisconnect as e:
            print("WebSocket connection closed by the client")
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(e)
    else:
        await ws.send_text(
            json.dumps({"type": "error", "body": {"message": "Que vosss?"}})
        )


@app.get("/file/{id}")
async def file(id: str) -> FileResponse:
    return FileResponse(path.join(settings["storage"], "%s.csv" % id))
