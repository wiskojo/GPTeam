import asyncio

import aiohttp
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from playwright.async_api import async_playwright
from readability import Document

from chat import Chat


async def scrape_text(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Set up a more complete user agent and viewport size
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )

        page = await context.new_page()

        try:
            await page.goto(url)

            # Add delay or wait for specific elements if necessary
            await asyncio.sleep(2)

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            return text
        finally:
            await browser.close()


async def scrape_links(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Check if the response contains an HTTP error
            if response.status >= 400:
                return "error"

            text = await response.text()

    soup = BeautifulSoup(text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup)

    return format_hyperlinks(hyperlinks)


def extract_hyperlinks(soup):
    hyperlinks = []
    for link in soup.find_all("a", href=True):
        hyperlinks.append((link.text, link["href"]))
    return hyperlinks


def format_hyperlinks(hyperlinks):
    formatted_links = []
    for link_text, link_url in hyperlinks:
        formatted_links.append(f"{link_text} ({link_url})")
    return formatted_links


def split_text(text, max_length=3000):
    paragraphs = text.split("\n")
    current_length = 0
    current_chunk = []

    for paragraph in paragraphs:
        if current_length + len(paragraph) + 1 <= max_length:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1
        else:
            yield "\n".join(current_chunk)
            current_chunk = [paragraph]
            current_length = len(paragraph) + 1

    if current_chunk:
        yield "\n".join(current_chunk)


def create_message(chunk, question):
    return f'"""{chunk}""" Using the above text, please answer the following question: "{question}" -- if the question cannot be answered using the text, please summarize the text.'


async def summarize_text(text, question, verbose=False):
    if not text:
        return "Error: No text to summarize"

    get_summaries = []
    chunks = list(split_text(text))

    for chunk in chunks:
        chat = Chat(model_name="gpt-3.5-turbo", max_tokens=300, verbose=verbose)
        message = create_message(chunk, question)

        chat.add_user_message(message)
        get_sumary = chat.get_chat_response()
        get_summaries.append(get_sumary)

    summaries = await asyncio.gather(*get_summaries)
    combined_summary = "\n".join(summaries)

    chat = Chat(model_name="gpt-3.5-turbo", max_tokens=1000, verbose=verbose)
    message = create_message(combined_summary, question)

    chat.add_user_message(message)
    final_summary = await chat.get_chat_response()
    return final_summary
