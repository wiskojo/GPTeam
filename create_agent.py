import argparse
import asyncio

import zmq
import zmq.asyncio

from agent import Agent


async def listen_for_messages(agent):
    while True:
        message = await agent.dealer.recv_string()
        await agent.handle_message(
            message
        )  # TODO: If you use asyncio.create_task here and not synchronously handle the message queue, many race conditions will cause duplicate work.


async def main(args):
    context = zmq.asyncio.Context()
    dealer = context.socket(zmq.DEALER)
    dealer.identity = str(args.agent_id).encode()
    dealer.connect("tcp://localhost:5555")

    print(f"Agent {args.agent_id} is connected")

    agent = Agent(
        name=args.agent_id, prompt=args.prompt, dealer=dealer, superior=args.superior
    )

    # Send the initial message based on the command line argument
    if args.task:
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
        nargs="?",
        help="Initial message to send to the agent containing the task",
    )
    parser.add_argument(
        "superior",
        type=str,
        help="Name of the superior agent/user",
    )

    args = parser.parse_args()

    asyncio.run(main(args))
