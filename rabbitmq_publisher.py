import json
import pika
import os
import logging

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def publish_user_created(user_id: str, username: str, email: str) -> None:
    connection = None
    logger.info(
        "[EVENT:PUBLISH] user_created | user_id=%s username=%s",
        user_id, username
    )
    try:
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=3,
            retry_delay=1
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue="user_created", durable=True)

        event = {
            "user_id": user_id,
            "username": username,
            "email": email
        }

        channel.basic_publish(
            exchange="",
            routing_key="user_created",
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        print(f"UserCreated event published for {username}")
        logger.info("[EVENT:PUBLISH] user_created sent successfully")

    except pika.exceptions.AMQPConnectionError:
        print("ERROR: Could not connect to RabbitMQ.")
    except Exception as e:
        print(f"ERROR publishing user_created event: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
