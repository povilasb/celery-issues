import amqp


def publish_to_nowhere(channel: amqp.Channel) -> None:
    print("[publish_to_nowhere] sending task to non-existant queue/exchange")
    channel.basic_publish(amqp.Message("my_task1"), routing_key="nowhere", exchange="nowhere")


def my_task1(channel: amqp.Channel) -> None:
    print("[my_task1] Calling my_task2.")
    channel.basic_publish(amqp.Message("my_task2"), routing_key="queue1")
    print("[my_task1] done")

def my_task2(channel: amqp.Channel) -> None:
    print("[my_task2] here")


_TASKS = {
    "publish_to_nowhere": publish_to_nowhere,
    "my_task1": my_task1,
    "my_task2": my_task2,
}


with amqp.Connection('127.0.0.1', confirm_publish=True) as amqp_conn:
    ch: amqp.Channel = amqp_conn.channel()
    ch.queue_declare("queue1")

    def on_message(msg: amqp.Message) -> None:
        print("[worker] received message:", msg.body)
        ch.basic_ack(msg.delivery_tag)

        if task := _TASKS.get(msg.body):
            task(ch)
        else:
            print("[worker] unknown task:", msg.body)

    ch.basic_consume(queue="queue1", callback=on_message)

    print("Listening for AMQP messages.")
    while True:
        amqp_conn.drain_events()

