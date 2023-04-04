import argparse
import asyncio

import zmq
import zmq.asyncio

from agent import Agent


async def listen_for_messages(agent):
    while True:
        message = await agent.dealer.recv_string()
        asyncio.create_task(agent.handle_message(message))


async def main(args):
    context = zmq.asyncio.Context()
    dealer = context.socket(zmq.DEALER)
    dealer.identity = str(args.agent_id).encode()
    dealer.connect("tcp://localhost:5555")

    print(f"Agent {args.agent_id} is connected")

    agent = Agent(name=args.agent_id, prompt=args.prompt, dealer=dealer)

    # Send the initial message based on the command line argument
    await dealer.send_multipart([dealer.identity, args.task.encode()])

    # Start the listening task
    await listen_for_messages(agent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an agent subprocess with a specific ID, prompt, and task."
    )
    parser.add_argument("agent_id", type=str, help="Agent ID")
    parser.add_argument(
        "prompt", type=str, help="System message to prompt the agent with"
    )
    parser.add_argument(
        "task",
        type=str,
        help="Initial message to send to the agent containing the task",
    )

    args = parser.parse_args()

    asyncio.run(main(args))
