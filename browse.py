import asyncio

import aiohttp
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from readability import Document

from chat import Chat


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}


async def scrape_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            # Check if the response contains an HTTP error
            if response.status >= 400:
                return "Error: HTTP " + str(response.status) + " error"

            text = await response.text()

    soup = BeautifulSoup(text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text


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


async def summarize_text(text, goal, is_website=True, verbose=False):
    # If text is sufficiently short just return it
    if len(text) < 1000:
        return text

    if text == "":
        return "Error: No text to summarize"

    get_summaries = []
    chunks = list(split_text(text))

    for chunk in chunks:
        chat = Chat(model_name="gpt-3.5-turbo", max_tokens=300, verbose=verbose)

        if is_website:
            message = (
                "Summarize the following website text using bullet points, do not describe the general website, but instead concisely extract the specifc information and relevant details this part of the page contains. If this part is just navigation, then mention that and don't waste time describing it.: "
                + chunk
            )
        else:
            message = (
                "Summarize the following text using bullet points, focusing on extracting concise and specific information and relevant details: "
                + chunk
            )

        message = message[:4000]
        if goal:
            message += f"\n\nMake sure to extract all relevant info towards this objective: {goal}"

        chat.add_user_message(message)
        get_sumary = chat.get_chat_response()
        get_summaries.append(get_sumary)

    summaries = await asyncio.gather(*get_summaries)

    combined_summary = "\n".join(summaries)

    chat = Chat(model_name="gpt-3.5-turbo", max_tokens=1000, verbose=verbose)

    # Summarize the combined summary
    message = (
        "Summarize the following list of bullet points by distilling it into only the important bullet points, focusing on extracting concise and specific infomation and relevant details: "
        + combined_summary
    )

    message = message[:4000]
    if goal:
        message += (
            f"\n\nMake sure to extract all relevant info towards this objective: {goal}"
        )

    chat.add_user_message(message)
    final_summary = await chat.get_chat_response()
    return final_summary
