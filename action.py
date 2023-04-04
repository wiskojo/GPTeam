from typing import Any, Dict, List
from pydantic import BaseModel
from zmq import Socket


import json


class Action(BaseModel):
    name: str
    args: Dict[str, Any]


def parse_actions(outputs: str) -> List[Action]:
    try:
        parsed = json.loads(outputs)
        actions = []
        for output in parsed:
            actions.append(
                Action(
                    name=output["action"].get("name"),
                    args=output["action"].get("args", {}),
                )
            )
        return actions
    except:
        print(f"LLM Output Parsing Error:\n{outputs}")


class ActionExecutor:
    def __init__(self, dealer: Socket):
        self.dealer = dealer

    async def execute_action(self, action: Action) -> None:
        if action.name == "noop":
            pass
        elif action.name == "create_agent":
            pass
        elif action.name == "message_parent":
            pass
        elif action.name == "message_children":
            pass
        elif action.name == "message_user":
            pass
        elif action.name == "finish":
            pass
        elif action.name == "google":
            pass
        elif action.name == "browse_website":
            pass
        elif action.name == "read_file":
            pass
        elif action.name == "write_file":
            pass
        elif action.name == "append_file":
            pass
        elif action.name == "delete_file":
            pass
        elif action.name == "write":
            pass
        else:
            pass
