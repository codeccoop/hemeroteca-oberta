# VENDOR
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# SOURCE
from scrapper import scrapper

app = FastAPI()

app.mount("/", StaticFiles(directory="static"), name="static")


class Query (BaseModel):
    word: str
    start_date: str
    end_date: str


@app.post("/query")
async def query (query: Query):
    f = scrapper(query.word, query.start_date, query.end_date)

    response = StreamingResponse(iter(f.read()), media_type="text/csv")
    return response
