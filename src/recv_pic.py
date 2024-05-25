import io

import click
from PIL import Image

from messages_pb2 import Response
from channel import Channel


class ImageChannel(Channel):
    def __init__(self, host: str, name: str, image: str):
        super().__init__(host, name)
        self.image = image
        self.reset_bin_content()

    def reset_bin_content(self):
        self.bin_content = b''

    def handle_receive(self, ch, method, properties, body):
        # Deserialize the response message received from the channel
        response = Response()
        response.ParseFromString(body)

        # Collect binary parts
        self.bin_content += response.binContent.data
        part_id = response.partId + 1
        total_parts = response.totalParts
        print(f"Received part {part_id} of {total_parts}")

        # Write the collected binary parts when we receive all the expected parts
        if part_id == total_parts:
            with open(self.image, "wb") as f:
                f.write(self.bin_content)
            image_stream = io.BytesIO(self.bin_content)
            img = Image.open(image_stream)
            img.show()
            self.reset_bin_content()


@click.command
@click.option("--broker", "-b", help="Address or hostname of the AMQP broker", default="localhost")
@click.option("--image", "-i", help="File name which the image will be written to", required=True)
@click.option("--chunks", "-c", help="Split the image to the number of chunks", default=1)
def main(broker: str, image: str, chunks: int):
    # Initialize the communication channel
    channel = ImageChannel(broker, "image", image)

    # Start gathering image parts
    channel.start_subscribe()


if __name__ == "__main__":
    main()
