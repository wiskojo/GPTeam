import zmq
from colorama import Fore
from colorama import init as colorama_init

colorama_init(autoreset=True)

COLORS = list(dict(Fore.__dict__.items()).values())


def main():
    context = zmq.Context()
    router = context.socket(zmq.ROUTER)

    port = 5555
    router.bind(f"tcp://*:{port}")
    print(f"Router is listening on port {port}")

    i = 0
    agent_id_to_color = {}

    try:
        while True:
            # Get the sender subprocess ID, target subprocess ID, and the message
            (
                from_agent_id,
                to_agent_id,
                message,
            ) = router.recv_multipart()[  # pylint:disable=E1136
                :3
            ]

            # Send the message to the target subprocess
            router.send_multipart([to_agent_id, message])

            from_agent_id = from_agent_id.decode("utf-8")
            to_agent_id = to_agent_id.decode("utf-8")
            message = message.decode("utf-8")

            for agent_id in (from_agent_id, to_agent_id):
                if agent_id not in agent_id_to_color:
                    agent_id_to_color[agent_id] = COLORS[i % len(COLORS)]
                    i += 1

            if from_agent_id != to_agent_id:
                print(
                    f"[{agent_id_to_color[from_agent_id]}{from_agent_id}{Fore.RESET} -> {agent_id_to_color[to_agent_id]}{to_agent_id}{Fore.RESET}]: {agent_id_to_color[from_agent_id]}{message}{Fore.RESET}"
                )

    except KeyboardInterrupt:
        print("Shutting down router")
    finally:
        router.close()
        context.term()


if __name__ == "__main__":
    main()
