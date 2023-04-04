from googlesearch import search
import requests
from bs4 import BeautifulSoup
from readability import Document


import aiohttp
from bs4 import BeautifulSoup
from chat import Chat


async def scrape_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
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


async def summarize_text(text, is_website=True, verbose=False):
    if text == "":
        return "Error: No text to summarize"

    if verbose:
        print("Text length: " + str(len(text)) + " characters")
    summaries = []
    chunks = list(split_text(text))

    for i, chunk in enumerate(chunks):
        if verbose:
            print("Summarizing chunk " + str(i + 1) + " / " + str(len(chunks)))
        chat = Chat(model_name="gpt-3.5-turbo", max_tokens=300, verbose=verbose)
        if is_website:
            message = (
                "Please summarize the following website text, do not describe the general website, but instead concisely extract the specifc information this subpage contains.: "
                + chunk
            )
        else:
            message = (
                "Please summarize the following text, focusing on extracting concise and specific information: "
                + chunk
            )

        chat.add_user_message(message[:4096])
        summary = await chat.get_chat_response()
        summaries.append(summary)

    if verbose:
        print("Summarized " + str(len(chunks)) + " chunks.")

    combined_summary = "\n".join(summaries)

    chat = Chat(model_name="gpt-3.5-turbo", max_tokens=300, verbose=verbose)

    # Summarize the combined summary
    if is_website:
        message = (
            "Please summarize the following website text, do not describe the general website, but instead concisely extract the specifc information this subpage contains.: "
            + combined_summary
        )
    else:
        message = (
            "Please summarize the following text, focusing on extracting concise and specific infomation: "
            + combined_summary
        )

    chat.add_user_message(message[:4096])
    final_summary = await chat.get_chat_response()
    return final_summary
