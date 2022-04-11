# About

This is a minimal working example that demonstrates an issue with error handling in
Celery tasks.
The problem is that an exception in one Celery task MAY break the execution of an
unrelated task.

This issue is present at `master` branch, `4.4.7`, `5.2.6`.

The respective branches of this repo conveniently have locked to before mentioned
Celery versions:

* [master](https://github.com/povilasb/celery-issues)
* [4.4.7](https://github.com/povilasb/celery-issues/tree/4.4.7)
* [5.2.6](https://github.com/povilasb/celery-issues/tree/5.2.6)

## How to run this?

1. `git fetch origin 4.4.7`
2. `git checkout 4.4.7`
3. `docker-compose up -d rabbitmq`
4. `poetry install`
5. `./worker.sh`
6. `poetry run python -m celery_issues.client`

## The issue explained

1. We send a `publish_to_nowhere` task to the worker.
2. This task is meant to error, but finishes successfully.
3. Then we send another task - `my_task1`.
4. `my_task1` calls another Celery task `my_task2`.
5. During this call Celery runtime will fail because of an error in a previous
   `publish_to_nowhere` task.
6. See the stack trace, but the issue stems from ampq library: `self.connection.drain_events(timeout=0)`

```py
[2022-04-11 14:40:31,518: INFO/MainProcess] Task celery_issues.celery.publish_to_nowhere[360700bf-0bdc-4ad9-acb5-f4fbfc24305b] received
[2022-04-11 14:40:31,519: WARNING/ForkPoolWorker-1] [publish_to_nowhere] sending task to non-existant queue/exchange
[2022-04-11 14:40:31,522: INFO/MainProcess] Task celery_issues.celery.my_task1[315f254f-bc1a-4b31-acb3-150e7386872e] received
[2022-04-11 14:40:31,559: INFO/ForkPoolWorker-1] Task celery_issues.celery.publish_to_nowhere[360700bf-0bdc-4ad9-acb5-f4fbfc24305b] succeeded in 0.03977871598908678s: None
[2022-04-11 14:40:31,562: WARNING/ForkPoolWorker-1] [my_task1] Calling my_task2.
[2022-04-11 14:40:31,584: ERROR/ForkPoolWorker-1] Task celery_issues.celery.my_task1[315f254f-bc1a-4b31-acb3-150e7386872e] raised unexpected: NotFound(404, "NOT_FOUND - no exchange 'noqueue' in vhost '/'", (60, 40), 'Basic.publish')
Traceback (most recent call last):
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/celery/app/trace.py", line 448, in trace_task
    R = retval = fun(*args, **kwargs)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/celery/app/trace.py", line 731, in __protected_call__
    return self.run(*args, **kwargs)
  File "/Users/povilas/projects/python/celery-issues/celery_issues/celery.py", line 15, in my_task1
    my_task2.apply_async()
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/celery/app/task.py", line 574, in apply_async
    return app.send_task(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/celery/app/base.py", line 787, in send_task
    amqp.send_task_message(P, name, message, **options)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/celery/app/amqp.py", line 510, in send_task_message
    ret = producer.publish(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/kombu/messaging.py", line 177, in publish
    return _publish(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/kombu/connection.py", line 523, in _ensured
    return fun(*args, **kwargs)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/kombu/messaging.py", line 199, in _publish
    return channel.basic_publish(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/channel.py", line 1791, in _basic_publish
    self.connection.drain_events(timeout=0)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 525, in drain_events
    while not self.blocking_read(timeout):
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 531, in blocking_read
    return self.on_inbound_frame(frame)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/method_framing.py", line 53, in on_frame
    callback(channel, method_sig, buf, None)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 537, in on_inbound_method
    return self.channels[channel_id].dispatch_method(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/abstract_channel.py", line 156, in dispatch_method
    listener(*args)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/channel.py", line 293, in _on_close
    raise error_for_code(
amqp.exceptions.NotFound: Basic.publish: (404) NOT_FOUND - no exchange 'noqueue' in vhost '/'
```

## py-amqp example

Since the issues is coming all the way from py-amqp library, I created a minimal code
to reproduce it:

```sh
poetry run python -m celery_issues.pyamqp_worker
poetry run python -m celery_issues.call_pyamqp
```

This will result in

```py
Listening for AMQP messages.
[worker] received message: publish_to_nowhere
[publish_to_nowhere] sending task to non-existant queue/exchange
[worker] received message: my_task1
[my_task1] Calling my_task2.
[worker] received message: my_task2
[my_task2] here
[my_task1] done
Traceback (most recent call last):
  File "/Users/povilas/.pyenv/versions/3.10.1/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/Users/povilas/.pyenv/versions/3.10.1/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/Users/povilas/projects/python/celery-issues/celery_issues/pyamqp_worker.py", line 42, in <module>
    amqp_conn.drain_events()
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 529, in drain_events
    while not self.blocking_read(timeout):
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 541, in blocking_read
    return self.on_inbound_frame(frame)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/method_framing.py", line 77, in on_frame
    callback(channel, msg.frame_method, msg.frame_args, msg)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 549, in on_inbound_method
    return self.channels[channel_id].dispatch_method(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/abstract_channel.py", line 157, in dispatch_method
    listener(*args)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/channel.py", line 1630, in _on_basic_deliver
    fun(msg)
  File "/Users/povilas/projects/python/celery-issues/celery_issues/pyamqp_worker.py", line 34, in on_message
    task(ch)
  File "/Users/povilas/projects/python/celery-issues/celery_issues/pyamqp_worker.py", line 6, in publish_to_nowhere
    channel.basic_publish(amqp.Message("my_task1"), routing_key="nowhere", exchange="nowhere")
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/channel.py", line 1821, in basic_publish_confirm
    self.wait([spec.Basic.Ack, spec.Basic.Nack],
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/abstract_channel.py", line 99, in wait
    self.connection.drain_events(timeout=timeout)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 529, in drain_events
    while not self.blocking_read(timeout):
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 541, in blocking_read
    return self.on_inbound_frame(frame)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/method_framing.py", line 53, in on_frame
    callback(channel, method_sig, buf, None)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/connection.py", line 549, in on_inbound_method
    return self.channels[channel_id].dispatch_method(
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/abstract_channel.py", line 157, in dispatch_method
    listener(*args)
  File "/Users/povilas/Library/Caches/pypoetry/virtualenvs/celery-issues-Q1iYfbHh-py3.10/lib/python3.10/site-packages/amqp/channel.py", line 294, in _on_close
    raise error_for_code(
amqp.exceptions.NotFound: Basic.publish: (404) NOT_FOUND - no exchange 'nowhere' in vhost '/'
```

So this closes the AMQP channel and, if not handled, connection as well.

Such behavior arguably is accepted by the AMQP library:

> Certain scenarios are assumed to be recoverable ("soft") errors in the protocol. They render the channel closed but applications can open another one and try to recover or retry a number of times. Most common examples are:

See <https://www.rabbitmq.com/channels.html#error-handling>

However, this should be handled by Celery/Kombu.
