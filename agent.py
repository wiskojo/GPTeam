from typing import Any, Dict, List
from pydantic import BaseModel
from colorama import Fore

import asyncio
import json
import aioconsole

from chat import Chat
from prompt import AGENT_PROMPT_SUFFIX


class Action(BaseModel):
    name: str
    args: Dict[str, Any]


class ActionHandler:
    async def handle(self, action: Action):
        if action.name == "noop":
            pass
        elif action.name == "create_agent":
            await self.create_agent(action.args)
        elif action.name == "message_parent":
            pass
        elif action.name == "message_children":
            pass
        elif action.name == "message_user":
            return await self.message_user(action.args)
        elif action.name == "finish":
            pass
        elif action.name == "google":
            pass
        elif action.name == "browse_website":
            pass
        elif action.name == "read_file":
            pass
        elif action.name == "write_file":
            pass
        elif action.name == "append_file":
            pass
        elif action.name == "delete_file":
            pass
        elif action.name == "write":
            return "Notes have been written down."
        else:
            pass

    async def create_agent(self, args):
        name = args["name"]
        prompt = args["prompt"]
        task = args["prompt"]

        chat = Chat(prompt=f"Your name is {name}.\n\n{prompt}\n\n{AGENT_PROMPT_SUFFIX}")
        agent = Agent(name=name, action_handler=ActionHandler(), chat=chat)
        await agent.enqueue_message(task)

        # Start the agents' listeners
        asyncio.create_task(agent.consume_action())
        asyncio.create_task(agent.consume_message())

        return agent

    async def message_user(self, args):
        return await aioconsole.ainput(args["message"])

    def parse_actions(self, outputs: str) -> List[Action]:
        try:
            parsed = json.loads(outputs)
            actions = []
            for e in parsed:
                actions.append(Action(name=e["action"]["name"], args=e["action"]["args"] if "args" in e["action"] else {}))
            return actions
        except:
            print(f"LLM Output Parsing Error:\n{outputs}")


class Agent:
    def __init__(
        self,
        name: str,
        action_handler: ActionHandler,
        chat: Chat,
    ):
        self.name = name
        self.chat = chat
        self.action_handler = action_handler
        self.action_queue = asyncio.Queue()
        self.message_queue = asyncio.Queue()

    async def enqueue_action(self, action: Action):
        await self.action_queue.put(action)

    async def _handle_action(self, action: Action):
        observation = await self.action_handler.handle(action)
        message = f"Finished executing action `{action.name}` with arguments: {action.args}. Results:\n\n{observation}"

        if observation is not None:
            await self.enqueue_message(message)

        with open(f"agent_{self.name}_logs.txt", "a") as f:
            f.write(f"Action handled by {self.name}: {action}\n\nOutput Message: {message}\n\n")
        # print(Fore.RED + f"Action handled by {self.name}: {action}\n\nOutput Message: {message}")

    async def enqueue_message(self, message: str):
        await self.message_queue.put(message)

    async def _handle_message(self, message: str):
        self.chat.add_user_message(message)
        outputs = await self.chat.get_chat_response()
        actions = self.action_handler.parse_actions(outputs)
        for action in actions:
            await self.enqueue_action(action)

        with open(f"agent_{self.name}_logs.txt", "a") as f:
            f.write(f"Message handled by {self.name}: {message}\n\nOutput Actions: {actions}\n\n")
        # print(Fore.GREEN + f"Message handled by {self.name}: {message}\n\nOutput Actions: {actions}")

    async def consume_action(self):
        while True:
            action = await self.action_queue.get()
            await self._handle_action(action)

    async def consume_message(self):
        while True:
            message = await self.message_queue.get()
            await self._handle_message(message)
