
import json

import pika
import pika.exceptions


class RabbitMQ:

    def __init__(self, url, exchange, queues):
        self._url = url
        self._exchange = exchange
        self._queues = queues
        self._connection = None
        self._channel = None

    def __enter__(self):
        self._connection = pika.BlockingConnection(
            pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._channel.close()
            self._connection.close()
        except (pika.exceptions.ChannelWrongStateError,
                pika.exceptions.StreamLostError):
            pass

    def declare(self):
        """
        Creation of exchange and queues.
        """
        # declare <exchange>
        self._channel.exchange_declare(exchange=self._exchange,
                                       exchange_type='direct')

        # declare and bind <queues>
        for k in self._queues.keys():
            self._channel.queue_declare(queue=self._queues[k])
            self._channel.queue_bind(queue=self._queues[k],
                                     exchange=self._exchange,
                                     routing_key=self._queues[k])

    def delete(self):
        """
        Deletion of exchange and queues.
        """
        # delete <queues>
        for k in self._queues.keys():
            try:
                self._channel.queue_purge(queue=self._queues[k])
                self._channel.queue_delete(queue=self._queues[k])
            except (pika.exceptions.ChannelClosedByBroker,
                    pika.exceptions.ChannelWrongStateError):
                pass

        try:
            # delete <exchange>
            self._channel.exchange_delete(exchange=self._exchange)
        except (pika.exceptions.ChannelClosedByBroker,
                pika.exceptions.ChannelWrongStateError):
            pass

    def publish(self, queue, data):
        """
        Publishing the message.

        :param queue: Queue name that is used as the routing key to bind on.
        :type queue: str
        :param data: Data that will be translated into the message body.
        :type data: list/dict
        """
        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=queue,
                                    body=json.dumps(data))

    def get(self, queue):
        """
        Get the message from the queue.

        :param queue: Queue name.
        :type queue: str
        :return: Data that is taken from the message body.
        :rtype: list/dict/None
        """
        try:
            method_frame, header_frame, output = \
                self._channel.basic_get(queue=queue)
        except pika.exceptions.DuplicateGetOkCallback:
            output = None
        except (pika.exceptions.ChannelClosedByBroker,
                pika.exceptions.ChannelWrongStateError):
            raise KeyboardInterrupt
        return output if not output else json.loads(output)
