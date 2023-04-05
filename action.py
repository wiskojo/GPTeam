import asyncio
import json
import os
from typing import Any, Dict, List

from pydantic import BaseModel
from zmq import Socket

import browse
from file_io import append_to_file, read_file, write_to_file


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
            task = write_to_file(action.args.get("file"), action.args.get("text"))
        elif action.name == "read_file":
            task = self._read_file(action.args)
        elif action.name == "append_to_file":
            task = append_to_file(action.args.get("file"), action.args.get("text"))
        elif action.name == "finish":
            task = self._finish(action.args)
        else:
            # TODO: Currently treating unrecognized actions as "no-op"
            pass

        if task:
            # TODO: Add exception handling here
            asyncio.create_task(task)

    async def _notify_task_completion(self, task_name, task_args, results):
        await self.dealer.send_multipart(
            [
                self.dealer.identity,
                f'Finished task "{task_name}" with arguments "{task_args}". Here are the results:\n\n{results}'.encode(),
            ]
        )

    async def _message_user(self, args: Dict[str, Any]):
        await self.dealer.send_multipart(
            [
                "user".encode(),
                args["message"].encode(),
            ]
        )

    async def _google(self, args: Dict[str, Any], num_results=8):
        # TODO: Should make this async
        search_results = list(browse.search(args["input"], num_results=num_results))
        await self._notify_task_completion(
            "google", json.dumps(args), json.dumps(search_results, ensure_ascii=False)
        )

    async def _browse_website(self, args: Dict[str, Any]):
        async def get_text_summary(url, goal=None):
            text = await browse.scrape_text(url)
            summary = await browse.summarize_text(text, goal)
            return """ "Result" : """ + summary

        async def get_hyperlinks(url):
            link_list = await browse.scrape_links(url)
            return link_list

        summary = await get_text_summary(args["url"], args["goal"])
        links = await get_hyperlinks(args["url"])

        # Limit links to 5
        if len(links) > 5:
            links = links[:5]

        result = f"""Website Content Summary: {summary}\n\nLinks: {links}"""

        await self._notify_task_completion("browse_website", json.dumps(args), result)

    async def _read_file(self, args: Dict[str, Any]):
        content = await read_file(args.get("file"))
        await self._notify_task_completion("read_file", json.dumps(args), content)

    async def _finish(self, args: Dict[str, Any]):
        await self._message_user({"message": args.get("results")})
        os._exit(0)  # pylint:disable=W0212
