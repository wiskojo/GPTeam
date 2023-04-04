import asyncio
from threading import Thread

import gradio as gr
import zmq
import zmq.asyncio

USER_ID = "user"

message_queue = asyncio.Queue()
history = []


async def listen_for_messages(dealer):
    while True:
        message = await dealer.recv_string()
        print(f"Received: {message}")
        await message_queue.put(message)


async def zmq_listener(identity):
    context = zmq.asyncio.Context()
    dealer = context.socket(zmq.DEALER)
    dealer.identity = identity.encode()
    dealer.connect("tcp://localhost:5555")

    print(f"Subprocess {identity} is connected")

    await listen_for_messages(dealer)


def run_zmq_listener(identity):
    asyncio.run(zmq_listener(identity))


def update_chat():
    while not message_queue.empty():
        message = message_queue.get_nowait()
        history.append([message, None])
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

    # send_button.click(send_message, textbox)

    demo.load(update_chat, None, chatbot, every=1)


if __name__ == "__main__":
    zmq_thread = Thread(target=run_zmq_listener, args=(USER_ID,))
    zmq_thread.start()

    demo.queue().launch()
