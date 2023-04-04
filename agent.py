import asyncio

from aiofile import async_open
from zmq import Socket

from action import Action, ActionExecutor, parse_actions
from chat import Chat


class Agent:
    def __init__(self, name: str, prompt: str, dealer: Socket):
        self.name = name
        self.prompt = prompt
        self.dealer = dealer
        self.chat = Chat(prompt=prompt)
        self.executor = ActionExecutor(dealer=dealer)

    async def handle_message(self, message: str):
        self.chat.add_user_message(message)
        response = await self.chat.get_chat_response()

        async with async_open(f"logs/{self.name}.log", "a") as afp:
            await afp.write(f"Input:\n{message}\n\nOutput:\n{response}\n\n")

        actions = parse_actions(response)
        if actions is None:
            await self.dealer.send_multipart(
                [
                    self.dealer.identity,
                    "Your response could not be parsed into the JSON format using json.loads. Please make sure you follow the format strictly.".encode(),
                ]
            )
        else:
            asyncio.gather(*[self.handle_action(action) for action in actions])

    async def handle_action(self, action: Action):
        await self.executor.execute_action(action)
