import asyncio
from threading import Thread

import gradio as gr
import zmq
import zmq.asyncio

USER_ID = "user"

message_queue = asyncio.Queue()
history = [
    [
        None,
        "Hi there! I'm here to help you with any tasks you need assistance with. Just let me know what you'd like me to do, and I'll be more than happy to help!",
    ]
]


async def listen_for_messages(dealer):
    while True:
        message = await dealer.recv_string()
        await message_queue.put(message)


async def zmq_listener():
    await listen_for_messages(dealer)


def run_zmq_listener():
    asyncio.run(zmq_listener())


async def zmq_send_message(message):
    await dealer.send_multipart(
        [
            "LeaderGPT".encode(),  # TODO: Don't hardcode this
            message.encode(),
        ]
    )


def send_message(message):
    history.append([message, None])
    asyncio.run(zmq_send_message(message))


def update_chat():
    while not message_queue.empty():
        message = message_queue.get_nowait()
        history.append([None, message])
    return history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()

    with gr.Row():
        with gr.Column(scale=9):
            textbox = gr.Textbox(
                show_label=False, placeholder="Enter text and press enter"
            ).style(container=False)
        with gr.Column(scale=1, min_width=0):
            send_button = gr.Button("➤", variant="primary")

    textbox.submit(send_message, textbox)
    textbox.submit(lambda: "", None, textbox)

    send_button.click(send_message, textbox)
    send_button.click(lambda: "", None, textbox)

    demo.load(update_chat, None, chatbot, every=1)


if __name__ == "__main__":
    context = zmq.asyncio.Context()
    dealer = context.socket(zmq.DEALER)
    dealer.identity = USER_ID.encode()
    dealer.connect("tcp://localhost:5555")

    print(f"Subprocess {USER_ID} is connected")

    zmq_thread = Thread(target=run_zmq_listener)
    zmq_thread.start()

    demo.queue().launch()
