import asyncio
import zmq
import zmq.asyncio
import argparse

from chat import Chat


async def listen_for_messages(dealer):
    while True:
        message = await dealer.recv_string()
        print("Message received:", message)

        chat.add_user_message(message)
        response = await chat.get_chat_response()

        print("Message response:", response)

        # TODO: Chat goes here to get action response
        # TODO: Output gets parsed into actions
        # TODO: Actions get dispatched to executor

        # target_id = input("Enter target subprocess ID: ")
        # response = f"Subprocess {dealer.identity.decode()} says: {message}"
        # await dealer.send_multipart(
        #     [
        #         dealer.identity,
        #         target_id.encode(),
        #         response.encode(),
        #     ]
        # )


async def main(args):
    context = zmq.asyncio.Context()
    dealer = context.socket(zmq.DEALER)
    dealer.identity = str(args.agent_id).encode()
    dealer.connect("tcp://localhost:5555")

    print(f"Agent {args.agent_id} is connected")

    # Send the initial message based on the command line argument
    await dealer.send_multipart([dealer.identity, args.task.encode()])

    # Start the listening task
    await listen_for_messages(dealer)


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

    chat = Chat(prompt=args.prompt)

    asyncio.run(main(args))
