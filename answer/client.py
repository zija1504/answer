# -*- coding: utf-8 -*-

import asyncio
import concurrent.futures
from typing import Any, Dict

import httpx

from answer.scraper import parse_links, parse_to_text

SEARCH_URLS = {"google": "https://google.com/search"}
URL = 'stackoverflow.com'


async def get_links(query):
    async with httpx.AsyncClient() as client:
        loop = asyncio.get_running_loop()
        query_param: Dict[str, str] = {"q": [query, {"site": URL}]}
        res = await client.get("https://google.com/search", params=query_param)
        text = res.text
        with concurrent.futures.ProcessPoolExecutor() as pool:
            results = await loop.run_in_executor(pool, parse_links, text)
            return results


def format_answer(link: str, text: str, indent: int = 4, char: str = "*"):
    answer = f"{char*10} {link} {char*10}"
    answer += "\n"
    # text = text.rjust(indent) + "\n\n"
    print(answer)
    print(text)


async def async_parser_for_links(link, args):
    loop = asyncio.get_running_loop()
    async with httpx.AsyncClient() as client:
        res = await client.get(link)
        text = res.text
        with concurrent.futures.ProcessPoolExecutor() as pool:
            results = await loop.run_in_executor(pool, parse_to_text, text, args)
            return results


async def runner(args):
    links = await get_links(args['query'])
    links = links[:10]
    corutine = await asyncio.gather(*(async_parser_for_links(link, args) for link in links))
    return corutine
