from typing import Any, Dict, List
from pydantic import BaseModel
from zmq import Socket
import asyncio

import json
import aioconsole


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
        print(f"LLM Output Parsing Error:\n{outputs}")


class ActionExecutor:
    def __init__(self, dealer: Socket):
        self.dealer = dealer

    async def execute_action(self, action: Action) -> None:
        task = None

        if action.name == "message_user":
            task = self._message_user(action.args)
        elif action.name == "google":
            pass
        elif action.name == "browse_website":
            pass
        elif action.name == "write_to_file":
            pass
        elif action.name == "read_file":
            pass
        elif action.name == "append_to_file":
            pass
        elif action.name == "add_memory":
            pass
        elif action.name == "recall_memory":
            pass
        elif action.name == "finish":
            pass
        else:
            pass

        if task:
            asyncio.create_task(task)

    async def _message_user(self, args: Dict[str, Any]):
        user_message = await aioconsole.ainput(f"{args['message']}:\n")
        await self.dealer.send_multipart(
            [
                self.dealer.identity,
                user_message.encode(),
            ]
        )
