from typing import Any, Dict, List
from pydantic import BaseModel
from zmq import Socket
import asyncio

import json
import aioconsole
import browse


class Action(BaseModel):
    name: str
    args: Dict[str, Any]


def parse_actions(outputs: str) -> List[Action]:
    try:
        parsed = json.loads(outputs)
        actions = []
        for output in parsed:
            actions.append(
                Action(
                    name=output["action"].get("name"),
                    args=output["action"].get("args", {}),
                )
            )
        return actions
    except:
        return None


class ActionExecutor:
    def __init__(self, dealer: Socket):
        self.dealer = dealer

    async def execute_action(self, action: Action) -> None:
        task = None

        if action.name == "message_user":
            task = self._message_user(action.args)
        elif action.name == "google":
            task = self._google(action.args)
        elif action.name == "browse_website":
            task = self._browse_website(action.args)
        elif action.name == "write_to_file":
            pass
        elif action.name == "read_file":
            pass
        elif action.name == "append_to_file":
            pass
        elif action.name == "finish":
            pass
        else:
            pass

        if task:
            # TODO: Add exception handling here
            asyncio.create_task(task)

    async def _message_user(self, args: Dict[str, Any]):
        pass
        # TODO: This doesn't work because there can be many overlapping messages sent to the user at the same time
        # user_message = await aioconsole.ainput(f"{args['message']}:\n")
        # await self.dealer.send_multipart(
        #     [
        #         self.dealer.identity,
        #         ("Message from user:\n\n" + user_message).encode(),
        #     ]
        # )

    async def _google(self, args: Dict[str, Any], num_results=8):
        # TODO: Should make this async
        search_results = list(browse.search(args["input"], num_results=num_results))
        await self.dealer.send_multipart(
            [
                self.dealer.identity,
                (
                    "Result from google:\n\n"
                    + json.dumps(search_results, ensure_ascii=False)
                ).encode(),
            ]
        )

    async def _browse_website(self, args: Dict[str, Any]):
        async def get_text_summary(url):
            text = await browse.scrape_text(url)
            summary = await browse.summarize_text(text)
            return """ "Result" : """ + summary

        async def get_hyperlinks(url):
            link_list = await browse.scrape_links(url)
            return link_list

        summary = await get_text_summary(args["url"])
        links = await get_hyperlinks(args["url"])

        # Limit links to 5
        if len(links) > 5:
            links = links[:5]

        result = f"""Website Content Summary: {summary}\n\nLinks: {links}"""

        await self.dealer.send_multipart(
            [
                self.dealer.identity,
                ("Result from browse_website:\n\n" + result).encode(),
            ]
        )
