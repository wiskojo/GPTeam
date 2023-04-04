import subprocess
import time

from prompt import ORCHESTRATOR_PROMPT


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
            "OrchestratorGPT",
            ORCHESTRATOR_PROMPT,
            "plan a budget vacation for a family of 4 to France, June 2023, Budget 5k, 1 week vacay",
        ]
    )
    print("Agent subprocess started")

    try:
        # Wait for the agent subprocess to finish
        agent_process.wait()
    except KeyboardInterrupt:
        print("Terminating agent and router subprocesses")
        agent_process.terminate()
        router_process.terminate()


if __name__ == "__main__":
    main()
