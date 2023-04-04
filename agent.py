from action import parse_actions, ActionExecutor, Action
from chat import Chat
from zmq import Socket


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
        actions = parse_actions(response)
        if actions:
            for action in actions:
                await self.handle_action(action)

    async def handle_action(self, action: Action):
        await self.executor.execute_action(action)
