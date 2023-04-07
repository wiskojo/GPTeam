import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List

from pydantic import BaseModel

import browse
from file_io import append_to_file, read_file, write_to_file
from prompt import AGENT_PROMPT_SUFFIX


class Action(BaseModel):
    name: str
    args: Dict[str, Any]


def parse_actions(outputs: str) -> List[Action]:
    try:
        parsed = json.loads(outputs)
        actions = []
        for output in parsed["actions"]:
            actions.append(
                Action(
                    name=output.get("name"),
                    args=output.get("args", {}),
                )
            )
        return actions
    except:
        return None


class ActionExecutor:
    def __init__(self, agent):
        self.agent = agent

    async def execute_action(self, action: Action) -> None:
        task = None

        if action.name == "message":
            task = self._message(action.args)
        elif action.name == "google":
            task = self._google(action.args)
        elif action.name == "browse_website":
            task = self._browse_website(action.args)
        elif action.name == "write_to_file":
            task = self._write_to_file(action.args)
        elif action.name == "read_file":
            task = self._read_file(action.args)
        elif action.name == "append_to_file":
            task = self._append_to_file(action.args)
        elif action.name == "create_agent":
            task = self._create_agent(action.args)
        elif action.name == "finish":
            task = self._finish(action.args)
        else:
            await self.agent.dealer.send_multipart(
                [
                    self.agent.dealer.identity,
                    f'The action "{action.name}" is not among the available options. Please attempt a different action.'.encode(),
                ]
            )

        if task:
            results = await asyncio.gather(task, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    await self.agent.dealer.send_multipart(
                        [
                            self.agent.dealer.identity,
                            f'Failed task "{action.name}" with arguments "{json.dumps(action.args)}". Here is the error:\n\n{result}'.encode(),
                        ]
                    )

    async def _notify_task_completion(self, task_name, task_args, results):
        await self.agent.dealer.send_multipart(
            [
                self.agent.dealer.identity,
                f'Finished task "{task_name}" with arguments "{task_args}". Here are the results:\n\n{results}'.encode(),
            ]
        )

    async def _message(self, args: Dict[str, Any]):
        if args["to"] != "user":
            message = f"(Message from {self.agent.name}) {args['message']}"
        else:
            message = args["message"]

        # TODO: Hacky hard-coded logic to ensure non leader agents can't talk to users directly
        if args["to"] == "user" and self.agent.name != "LeaderGPT":
            await self.agent.dealer.send_multipart(
                [
                    self.agent.dealer.identity,
                    "You cannot message the user directly, please work with your superior agent to carry out your task.".encode(),
                ]
            )
            return

        await self.agent.dealer.send_multipart(
            [
                args["to"].encode(),
                message.encode(),
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
            return summary

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

    async def _write_to_file(self, args: Dict[str, Any]):
        await write_to_file(args.get("file"), args.get("text"))
        await self._notify_task_completion(
            "write_to_file",
            json.dumps(args),
            f"File {args.get('file')} successfully written to.",
        )

    async def _append_to_file(self, args: Dict[str, Any]):
        await append_to_file(args.get("file"), args.get("text"))
        await self._notify_task_completion(
            "append_to_file",
            json.dumps(args),
            f"File {args.get('file')} successfully appended to.",
        )

    async def _create_agent(self, args: Dict[str, Any]):
        subprocess.Popen(
            [
                "python",
                "create_agent.py",
                args.get("name"),
                args.get("prompt") + AGENT_PROMPT_SUFFIX,
                f"(Message from {self.agent.name}) {args.get('message')}",
                self.agent.name,
            ]
        )
        self.agent.subordinates.add(args.get("name"))
        await self._notify_task_completion(
            "create_agent",
            json.dumps(args),
            f"Agent {args.get('name')} successfully created.",
        )

    async def _finish(self, args: Dict[str, Any]):
        # TODO: This introduces a race condition, if multiple actions are issued and finish finishes first, the rest won't get executed
        await self._message({"to": self.agent.superior, "message": args.get("results")})
        # TODO: Somehow need to remove from superior's subordinates list
        os._exit(0)  # pylint:disable=W0212
