import psutil
import os
from celery import Celery
from celery.canvas import Signature
import gc
import objgraph
import random


app = Celery(broker='amqp://guest:guest@localhost:5672/', backend='rpc://')


@app.task(name='hello')
def hello(foo):
    return foo


def get_mem_usage():
    gc.collect()
    process = psutil.Process(os.getpid())
    n = process.memory_info().rss
    print(f"memory usage: {n}")
    objgraph.show_growth(limit=3)


def run_task():
    bigstr = "x" * 1000 * 1000 * random.randint(1, 6)
    r = app.send_task('hello', args=(bigstr,), chain=[Signature('hello')])
    assert r.get()


if __name__ == "__main__":
    get_mem_usage()
    for _ in range(10):
        for _ in range(3):
            run_task()
        get_mem_usage()
