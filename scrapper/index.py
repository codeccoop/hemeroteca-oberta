# BUILT-INS
import re
import os.path
from os import unlink
from pathlib import Path
import random
from datetime import datetime as dt
import time
from typing import List
import io

# VENDOR
import requests
from urllib.parse import urlencode
from lxml import html


def get_url(word: str, start_date: str, end_date: str, page: int = 1) -> str:
    schema = "http"
    domain = "hemeroteca.lavanguardia.com"
    path = "search.html"

    sd = dt.strptime(start_date, "%d-%m-%Y")
    ed = dt.strptime(end_date, "%d-%m-%Y")

    query = {
        "q": word,
        "bd": sd.day,
        "bm": sd.month,
        "by": sd.year,
        "ed": sd.day,
        "em": sd.month,
        "ey": sd.year,
        "page": page,
        "keywords": "",
        "__checkbox_home": "true",
        "edition": "",
        "exclude": "",
        "x": "24",
        "y": "11",
        "excludeAds": "false",
        "sortBy": "date",
        "order": "asc"
    }

    return "{schema}://{domain}/{path}?{query}".format(
        schema=schema,
        domain=domain,
        path=path,
        query=urlencode(query)
    )


def get_page(word: str, start_date: str, end_date: str, page: int = 1, tries: int = 0) -> bytes:
    if tries >= 3:
        return b""

    url = get_url(word, start_date, end_date, page)
    try:
        res = requests.get(url)
        return res.content
    except requests.RequestException:
        time.sleep(random.randint(0, 3))
        return get_page(word, start_date, end_date, page, tries+1)


def get_records(tree: html.HtmlElement) -> List[dict]:
    records = tree.xpath(
        "div[@class=\"contentSeccio\"]/ul[@class=\"destacat\"]/li")
    if len(records) == 0:
        return []

    docs = []
    for record in records:
        doc = {
            "year": "",
            "month": "",
            "day": "",
            "cover": [record.xpath("a[@class=\"portada\"]/img/@src"), ""][0],
            "link": [record.xpath("a[@class=\"portada\"]/@href"), ""][0],
            "edition": [record.xpath("a[@class=\"edicion\"]/text()"), ""][0],
            "text": [record.xpath("p/text()"), ""][0]
        }

        date_match = re.search(
            r"(?<=preview\/)[0-9]{4}\/[0-9]{2}\/[0-9]{2}", doc["link"])
        if date_match:
            date = dt.strptime(date_match.group(), "%Y/%m/%d")
            doc["year"] = date.year
            doc["month"] = date.month
            doc["day"] = date.day

        docs.append(doc)

    return docs


def get_pages(tree: html.HtmlElement, acum: List[int] = []) -> List[int]:
    paginator = tree.xpath("//div[@class=\"pagines\"]/span/a/text()")

    pages = []
    for page in paginator:
        try:
            page = int(page)
            if len(acum) > 0 and page not in acum and min(acum) < page:
                pages.append(page)
        except:
            pass

    return pages


def write_records(records: List[dict], fpath: str = "resultats.csv") -> None:
    if not os.path.isfile(fpath):
        Path(fpath).touch()

    with open(fpath, "a+") as fconn:
        fconn.seek(0, 0)
        if len(fconn.read(2)) == 0:
            fconn.write("any,mes,dia,edicio,text,enlaç,portada\n")

        fconn.seek(0, 2)
        for record in records:
            fconn.write(re.sub(
                r"(\r|\n)", "", "{year},{month},{day},{edition},{text},{link},{cover}".format(**record)))


def main(word: str = "lavadora", start_date: str = "01-01-1950", end_date: str = "31-12-1979",
         output_path: str = "resultats.csv") -> io.TextIOWrapper:
    import pdb; pdb.set_trace()
    page_content = get_page(word, start_date, end_date)
    tree = html.fromstring(page_content)
    records = get_records(tree)
    write_records(records)
    pages = get_pages(tree)

    while len(pages):
        page = pages.pop(0)
        page_content = get_page(word, start_date, end_date, page)
        tree = html.fromstring(page_content)
        records = get_records(tree)
        write_records(records)
        pages = get_pages(tree, acum=pages)

    return open(output_path, "r")


if __name__ == "__main__":
    main()
