import asyncio

from aiofile import async_open
from zmq import Socket

from action import Action, ActionExecutor, parse_actions
from chat import Chat


class Agent:
    def __init__(self, name: str, prompt: str, dealer: Socket, superior: str):
        self.name = name
        self.prompt = prompt
        self.dealer = dealer
        self.chat = Chat(prompt=prompt)
        self.executor = ActionExecutor(agent=self)

        self.superior = superior
        self.subordinates = set()

    async def handle_message(self, message: str):
        org_struct_message = f"Your Organizational Structure:\nYou are: {self.name}\nYour Superior Agent is: {self.superior}\nYour Subordinate Agents are: {list(self.subordinates)}"
        self.chat.add_system_message(org_struct_message)
        self.chat.add_user_message(message)
        response = await self.chat.get_chat_response()

        async with async_open(f"logs/{self.name}.txt", "a") as afp:
            await afp.write(f"Input:\n{message}\n\nOutput:\n{response}\n\n")

        actions = parse_actions(response)
        if actions is None:
            await self.dealer.send_multipart(
                [
                    self.dealer.identity,
                    f"Your response could not be parsed into the JSON format using json.loads. Please make sure you follow the format strictly:\n{response}".encode(),
                ]
            )
        else:
            asyncio.gather(*[self.handle_action(action) for action in actions])

    async def handle_action(self, action: Action):
        await self.executor.execute_action(action)
