import time
from abc import abstractmethod

import pika

from messages_pb2 import Response


class Channel:
    def __init__(self, host: str, name: str):
        self.name_ = name
        self.host_ = host
        self._connect()
        self._configure_channel()

    def _connect(self):
        connected = False
        while not connected:
            try:
                self.connection_ = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host_))
                connected = True
                print("Connected")
            except pika.exceptions.AMQPConnectionError:
                # Wait for 5 secs before trying to connect again
                print("Attempt to connect to RabbitMQ. Reconnecting in 5 seconds...")
                time.sleep(5)
        self.channel_ = self.connection_.channel()

    def _configure_channel(self):
        # Enable Publisher Confirms
        self.channel_.confirm_delivery()
        # Declare a durable queue
        self.channel_.queue_declare(queue=self.name_, durable=True)

    def send_response(self, response: Response):
        try:
            self.channel_.basic_publish(
                exchange='', routing_key=self.name_, body=response.SerializeToString(),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,  # make message persistent
                ))
        except pika.exceptions.UnroutableError:
            # When the sender doesn't receive confirmation from RabbitMQ.
            # Example: The sender got disconnected in the middle of transmitting a message.
            # We can implement a mechnism to stash and re-send the message here.
            print("Unable to send message to RabbmitMQ.")

    @abstractmethod
    def handle_response(self, ch, method, properties, body):
        raise NotImplementedError()

    def start_subscribe(self):
        def handle_receive(ch, method, properties, body):
            # Deserialize the response message received from the channel
            response = Response()
            response.ParseFromString(body)
            # Call the callback to handle response
            self.handle_response(response)

        while True:
            try:
                self.channel_.basic_consume(
                    queue=self.name_, on_message_callback=handle_receive, auto_ack=True)
                print("Start consuming.")
                self.channel_.start_consuming()
            except pika.exceptions.ConnectionClosedByBroker:
                print("Connection to RabbitMQ closed.")
                self._connect()
            except pika.exceptions.StreamLostError:
                print("Stream lost error occurred.")
                self._connect()
            except Exception as e:
                print("Unexpected error occurred.")
                self._connect()
