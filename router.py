import zmq


def main():
    context = zmq.Context()
    router = context.socket(zmq.ROUTER)

    port = 5555
    router.bind(f"tcp://*:{port}")
    print(f"Router is listening on port {port}")

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


if __name__ == "__main__":
    main()
