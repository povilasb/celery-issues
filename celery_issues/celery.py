from celery import Celery


app = Celery("demo_app", broker="pyamqp://guest@127.0.0.1//")


@app.task()
def my_task2():
    print("[my_task2] here")


@app.task()
def my_task1() -> None:
    print("[my_task1] Calling my_task2.")
    my_task2.apply_async()
    print("[my_task1] done")


@app.task()
def publish_to_nowhere() -> None:
    print("[publish_to_nowhere] sending task to non-existant queue/exchange")
    app.send_task("whatever", kwargs={}, exchange="noqueue", routing_key="noqueue")
