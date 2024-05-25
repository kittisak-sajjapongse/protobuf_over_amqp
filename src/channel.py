from abc import abstractmethod

import pika

from messages_pb2 import Response


class Channel:
    def __init__(self, host: str, name: str):
        self.name = name
        self.connection_ = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel_ = self.connection_.channel()
        self.channel_.queue_declare(queue=self.name)

    def send_response(self, response: Response):
        self.channel_.basic_publish(
            exchange='', routing_key=self.name, body=response.SerializeToString())

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

        self.channel_.basic_consume(
            queue=self.name, on_message_callback=handle_receive, auto_ack=True)
        self.channel_.start_consuming()
