from pathlib import Path

import click

from messages_pb2 import Response
from channel import Channel


def calculate_chunk_sizes(file_size: int, num_chunks: int) -> list[int]:
    chunk_size = file_size // num_chunks
    remainder = file_size % num_chunks
    chunk_sizes = [chunk_size] * num_chunks
    for i in range(remainder):
        chunk_sizes[i] += 1
    return chunk_sizes


@click.command
@click.option("--broker", "-b", help="Address or hostname of the AMQP broker", default="localhost")
@click.option("--image", "-i", help="File name of the image to send", required=True)
@click.option("--chunks", "-c", help="Split the image to the number of chunks", default=1)
def main(broker: str, chunks: int, image: str):
    image_file = Path(image)
    file_size = image_file.stat().st_size
    if not image_file.is_file():
        raise Exception("Cannot find specified image file")

    # Calculate the size of chunks
    chunk_sizes = calculate_chunk_sizes(file_size, chunks)

    # Load the image to be sent
    with open(str(image_file), "rb") as f:
        bin_content = f.read()

    # Create publish channel
    channel = Channel(broker, "image")

    s_offset = 0
    for i, chunk_size in enumerate(chunk_sizes):
        # Create a new message
        e_offset = s_offset + chunk_size
        response = Response()
        response.totalParts = chunks
        response.partId = i
        response.binContent.data = bin_content[s_offset:e_offset]
        s_offset += chunk_size

        # Serialize the message to a binary string
        print(f"Sending image part {i+1} of {chunks}")
        with open(f"object{i}.bin", "wb") as f:
            f.write(response.SerializeToString())

        # Publish the reponse
        channel.send_response(response)


if __name__ == "__main__":
    main()
