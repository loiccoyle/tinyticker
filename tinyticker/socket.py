import asyncio
import enum
import logging
import socket

from .paths import SOCKET_FILE
from .sequence import Sequence

LOGGER = logging.getLogger(__name__)


class Message(enum.Enum):
    NEXT = "next"
    PREVIOUS = "previous"


def send_message(message: Message):
    """Send a message to the tinyticker socket.

    Args:
        message: Message to send.
    """
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(str(SOCKET_FILE))
        sock.sendall(message.value.encode())


async def run_server(sequence: Sequence):
    """Run the server to listen for messages.

    Args:
        sequence: Sequence object to control.
    """

    async def handle_client(reader: asyncio.StreamReader, _):
        while True:
            data = await reader.read(100)
            if not data:
                break
            msg = data.decode()
            LOGGER.info("Received: %s", msg)
            if msg == Message.NEXT.value:
                if sequence is not None and sequence.current_index is not None:
                    sequence.go_to_index(
                        (sequence.current_index + 1) % len(sequence.tickers)
                    )
            elif msg == Message.PREVIOUS.value:
                if sequence is not None and sequence.current_index is not None:
                    sequence.go_to_index(
                        (sequence.current_index - 1) % len(sequence.tickers)
                    )
            else:
                LOGGER.warning("Unknown message:", msg)
            await asyncio.sleep(1)

    server = await asyncio.start_unix_server(handle_client, SOCKET_FILE)
    LOGGER.info("Server socket started: %s", SOCKET_FILE)
    async with server:
        await server.serve_forever()
