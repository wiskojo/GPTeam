from typing import Optional

from langchain.callbacks.base import AsyncCallbackManager
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from streaming_file_callback import StreamingFileCallbackHandler


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
        self.temperature = temperature
        self.verbose = verbose
        self.max_tokens = max_tokens
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

    def _get_chat(self):
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            streaming=True,
            callback_manager=AsyncCallbackManager([StreamingFileCallbackHandler()]),
            verbose=self.verbose,
            max_tokens=self.max_tokens,
            request_timeout=120,  # TODO: Maybe too high?
        )

    async def get_chat_response(self):
        response = await self._get_chat().agenerate(messages=[self.conversation])

        chat_response = response.generations[0][0].message.content
        self.add_assistant_message(chat_response)
        return chat_response
