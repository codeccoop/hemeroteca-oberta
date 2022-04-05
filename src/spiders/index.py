__all__ = ["WordSpider"]

# BUILT-INS
import re
import os.path
from os import unlink
from pathlib import Path
import random
from datetime import datetime as dt
from typing import List
import asyncio
import json
import math

# VENDOR
import aiohttp
import aiofiles
import aiofiles.os
from urllib.parse import urlencode
from lxml import html
from fastapi import WebSocket


def get_url(word: str, start_date: str, end_date: str, page: int = 1) -> str:
    schema = "http"
    domain = "hemeroteca.lavanguardia.com"
    path = "search.html"

    sd = dt.strptime(start_date, "%Y-%m-%d")
    ed = dt.strptime(end_date, "%Y-%m-%d")

    query = {
        "q": word,
        "bd": sd.day,
        "bm": sd.month,
        "by": sd.year,
        "ed": ed.day,
        "em": ed.month,
        "ey": ed.year,
        "page": page,
        "keywords": "",
        "__checkbox_home": "true",
        "edition": "",
        "exclude": "",
        "x": "24",
        "y": "11",
        "excludeAds": "false",
        "sortBy": "date",
        "order": "asc",
    }

    return "{schema}://{domain}/{path}?{query}".format(
        schema=schema, domain=domain, path=path, query=urlencode(query)
    )


async def get_page(
    word: str, start_date: str, end_date: str, page: int = 1, tries: int = 0
) -> bytes:
    if tries >= 3:
        return b""

    url = get_url(word, start_date, end_date, page)
    print("Request from <%s>" % url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status == 200:
                    return await res.content.read()
                else:
                    raise aiohttp.ClientError
    except aiohttp.ClientError:
        print("Can't reach the page <%s>" % url)
        await asyncio.sleep(random.randint(0, 5))
        print("Retry")
        return await get_page(word, start_date, end_date, page, tries + 1)


def get_records(tree: html.HtmlElement) -> List[dict]:
    records = tree.xpath('//div[@class="contentSeccio"]/ul[@class="destacat"]/li')
    if len(records) == 0:
        return []

    docs = []
    for record in records:
        doc = {
            "year": "",
            "month": "",
            "day": "",
            "cover": [*record.xpath('a[@class="portada"]/img/@src'), ""][0].strip(),
            "link": [*record.xpath('a[@class="portada"]/@href'), ""][0].strip(),
            "edition": [*record.xpath('a[@class="edicion"]/text()'), ""][0].strip(),
            "text": "".join(record.xpath("p/text()")).strip(),
        }

        date_match = re.search(
            r"(?<=preview\/)[0-9]{4}\/[0-9]{2}\/[0-9]{2}", doc["link"]
        )
        if date_match:
            date = dt.strptime(date_match.group(), "%Y/%m/%d")
            doc["year"] = date.year
            doc["month"] = date.month
            doc["day"] = date.day

        docs.append(doc)

    return docs


def get_pages(tree: html.HtmlElement, acum: List[int] = []) -> List[int]:
    paginator = tree.xpath('//div[@class="pagines"]/span/a/text()')

    pages = []
    for page in paginator:
        try:
            page = int(page)
            if len(acum) > 0 and page not in acum and min(acum) < page:
                pages.append(page)
        except:
            pass

    return acum + pages


def get_query_count(tree: html.HtmlElement) -> int:
    count = "".join(tree.xpath('//div[@class="searchInfo"]/strong[3]/text()'))
    if not count or len(count) == 0:
        return 0

    return math.ceil(int(count) / 9)


async def write_records(records: List[dict], fpath: str = "resultats.csv") -> None:

    if not os.path.isfile(fpath):
        Path(fpath).touch()

    async with aiofiles.open(fpath, "a+") as fconn:
        await fconn.seek(0, 0)
        if len(await fconn.read(2)) == 0:
            await fconn.write("any,mes,dia,edicio,text,enlaç,portada\n")

        await fconn.seek(0, 2)
        for record in records:
            await fconn.write(
                re.sub(
                    r"(\r|\n)",
                    "",
                    '{year},{month},{day},"{edition}","{text}",{link},{cover}'.format(
                        **record
                    ),
                )
                + "\n"
            )


async def crawl(
    ws: WebSocket,
    jobid: str,
    word: str,
    start_date: str,
    end_date: str,
) -> None:

    storage = "tmp/%s.csv" % jobid
    if os.path.exists(storage):
        if os.path.isfile(storage):
            await aiofiles.os.remove(storage)

    print("Search results for %s from %s to %s" % (word, start_date, end_date))
    page_content = await get_page(word, start_date, end_date)
    tree = html.fromstring(page_content)
    count = get_query_count(tree)
    records = get_records(tree)
    await write_records(records, storage)
    pages = get_pages(tree, [1])

    await ws.send_text(
        json.dumps({"type": "info", "body": {"word": word, "page": 1, "total": count}})
    )

    while len(pages) > 0:
        await asyncio.sleep(random.randint(0, 1))
        page = pages.pop(0)
        page_content = await get_page(word, start_date, end_date, page)
        tree = html.fromstring(page_content)
        records = get_records(tree)
        await write_records(records, storage)
        pages = get_pages(tree, acum=pages)
        print(pages)

        confirmation = await ws.receive_text()
        await ws.send_text(
            json.dumps(
                {"type": "info", "body": {"word": word, "page": page, "total": count}}
            )
        )

    await ws.send_text(
        json.dumps({"type": "event", "body": {"event": "closed", "fileId": jobid}})
    )


class WordSpider:
    async def crawl(
        self, ws: WebSocket, word: str, start_date: str, end_date: str
    ) -> None:
        jobid = "%s.%s.%s" % (word, start_date, end_date)
        await crawl(ws, jobid, word, start_date, end_date)
