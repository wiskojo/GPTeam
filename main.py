import subprocess
import time

from prompt import LEADER_PROMPT


def main():
    # Start the router as a subprocess
    router_process = subprocess.Popen(["python", "router.py"])
    print("Router subprocess started")

    # Give the router some time to start before launching the agent
    time.sleep(1)

    # Start the first agent as a subprocess
    agent_process = subprocess.Popen(
        [
            "python",
            "create_agent.py",
            "LeaderGPT",
            LEADER_PROMPT,
            "Help me and my family of 3 plan a vacation to France for next month with a budget of 5k USD",
            "user",
        ]
    )
    print("Agent subprocess started")

    # Start the chat UI
    chat_process = subprocess.Popen(
        [
            "python",
            "chat_ui.py",
        ]
    )
    print("Chat UI started")

    try:
        # Wait for the agent subprocess to finish
        agent_process.wait()
    finally:
        print("Terminating subprocesses")
        agent_process.terminate()
        router_process.terminate()
        chat_process.terminate()


if __name__ == "__main__":
    main()
