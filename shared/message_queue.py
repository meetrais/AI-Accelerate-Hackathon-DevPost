"""
RabbitMQ message queue for A2A communication
"""
import pika
import json
import os
from typing import Callable, Optional
from .protocols import A2AMessage


class MessageQueue:
    """RabbitMQ wrapper for A2A messages"""
    
    def __init__(self):
        rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://travel_user:travel_pass@localhost:5672')
        self.parameters = pika.URLParameters(rabbitmq_url)
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection"""
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        print("✓ Connected to RabbitMQ")
    
    def declare_queue(self, queue_name: str):
        """Declare a queue"""
        if not self.channel:
            self.connect()
        self.channel.queue_declare(queue=queue_name, durable=True)
    
    def publish(self, queue_name: str, message: A2AMessage):
        """Publish a message to a queue"""
        if not self.channel:
            self.connect()
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message.model_dump_json(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
    
    def consume(self, queue_name: str, callback: Callable):
        """Consume messages from a queue"""
        if not self.channel:
            self.connect()
        
        def wrapper(ch, method, properties, body):
            message_dict = json.loads(body)
            message = A2AMessage(**message_dict)
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper
        )
        
        print(f"✓ Consuming from queue: {queue_name}")
        self.channel.start_consuming()
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()


# Global instance
message_queue = MessageQueue()
