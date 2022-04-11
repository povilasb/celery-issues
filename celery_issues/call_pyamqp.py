import amqp

with amqp.Connection('127.0.0.1', confirm_publish=True) as c:
    ch: amqp.Channel = c.channel()
    ch.queue_declare("queue1")

    ch.basic_publish(amqp.Message("publish_to_nowhere"), routing_key="queue1")
    ch.basic_publish(amqp.Message("my_task1"), routing_key="queue1")

