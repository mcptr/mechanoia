import pika
import json


class Queue:
    def __init__(self, name, **kwargs):
        self.queue = name
        self.durable = kwargs.pop("durable", False)
        self.auto_delete = kwargs.pop("auto_delete", False)

    def as_dict(self):
        return self.__dict__


class TaskConsumer:
    def __init__(self, url, exchange, in_queue, **kwargs):
        self.url = url
        self.exchange = exchange
        self.in_queue = in_queue
        self.in_connection = pika.BlockingConnection(pika.URLParameters(url))
        self.in_channel = self.in_connection.channel()
        self.callback = kwargs.pop("callback", None)

        self.in_channel.exchange_declare(
            exchange=exchange.exchange,
            exchange_type=exchange.exchange_type,
        )

        self.in_channel.queue_declare(**self.in_queue.as_dict())

        self.in_channel.queue_bind(
            exchange=exchange.exchange,
            queue=self.in_queue.queue,
        )

    def __del__(self):
        self.in_channel.close()
        self.in_connection.close()

    def process(self, *args, **kwargs):
        if self.callback:
            self.callback(*args, **kwargs)
        else:
            print(args, kwargs)

    def start(self, callback=None):
        self.in_channel.basic_consume(
            (callback or self.process),
            queue=self.in_queue.queue
        )
        self.in_channel.start_consuming()


class TaskPublisher:
    def __init__(self, url, exchange, queue, **kwargs):
        self.url = url
        self.exchange = exchange
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.URLParameters(url))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=exchange.exchange,
            exchange_type=exchange.exchange_type,
        )

        self.channel.queue_declare(**self.queue.as_dict())

        self.channel.queue_bind(
            exchange=exchange.exchange,
            queue=self.queue.queue,
        )

        self.channel.basic_qos(prefetch_count=1)

    def __del__(self):
        self.channel.close()
        self.connection.close()

    def publish(self, message, **kwargs):
        properties = None
        if kwargs.pop("persistent", None):
            properties = pika.BasicProperties(
                delivery_mode=2,
            )

        self.channel.basic_publish(
            exchange=self.exchange.exchange,
            routing_key=self.queue.queue,
            body=json.dumps(message),
            properties=properties,
        )
        print("# PUBLISH:", json.dumps(message))


class TaskFilter:
    def __init__(self, input_config, output_config):
        self.consumer = TaskConsumer(*input_config)
        self.publisher = TaskPublisher(*output_config)

    def process(self, *args, **kwargs):
        print(args, kwargs)

    def start(self):
        self.consumer.start(self.process)
