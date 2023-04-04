import asyncio

from agent import Agent, ActionHandler
from chat import Chat
from prompt import ORCHESTRATOR_PROMPT


async def main():
    chat = Chat(prompt=ORCHESTRATOR_PROMPT, model_name='gpt-4')
    orchestrator = Agent(name="OrchestratorGPT", action_handler=ActionHandler(), chat=chat)
    await orchestrator.enqueue_message(
        "plan a budget vacation for a family of 4 to France, June 2023, Budget 5k, 1 week vacay"
    )

    # Start the agents' listeners
    asyncio.create_task(orchestrator.consume_action())
    asyncio.create_task(orchestrator.consume_message())

    # Run the event loop indefinitely
    await asyncio.Event().wait()


asyncio.run(main())
