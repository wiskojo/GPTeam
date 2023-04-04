from langchain.chat_models.openai import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional


class Chat:
    def __init__(
        self,
        prompt: str = "Assistant is a large language model trained by OpenAI.",
        model_name: str = "gpt-4",
        temperature: int = 0,
        verbose: bool = True,
        max_tokens: Optional[int] = None,
    ):
        self.model_name = model_name
        self.chat = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            streaming=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=verbose,
            max_tokens=max_tokens,
        )
        self.conversation = []

        if prompt:
            self.prompt = prompt
            self.add_system_message(prompt)

    def add_system_message(self, message: str):
        self.conversation.append(SystemMessage(content=message))

    def add_user_message(self, message: str):
        self.conversation.append(HumanMessage(content=message))

    def add_assistant_message(self, message: str):
        self.conversation.append(AIMessage(content=message))

    async def get_chat_response(self):
        response = await self.chat.agenerate(messages=[self.conversation])

        chat_response = response.generations[0][0].message.content
        self.add_assistant_message(chat_response)
        return chat_response
