import time
import psutil
import os
from celery import Celery
from celery.canvas import Signature
import gc
import objgraph
import random
import concurrent.futures


app = Celery(broker='amqp://guest:guest@localhost:5672/', backend='rpc://')


@app.task(name='hello')
def hello(foo):
    return foo


def get_mem_usage():
    # gc.collect()
    process = psutil.Process(os.getpid())
    n = process.memory_info().rss
    print(f"memory usage: {n}")
    objgraph.show_growth(limit=3)


def gen_big_str():
    return "x" * 1000 * 1000 * random.randint(1, 10)


def is_ready(result):
    return result.ready()


if __name__ == "__main__":
    LEAK = False
    with concurrent.futures.ThreadPoolExecutor() as executor:
        get_mem_usage()
        for _ in range(10):
            for _ in range(10):
                args = ({'foo': gen_big_str(), 'bar': [{'bla': gen_big_str()}]},)
                if LEAK:
                    future = executor.submit(app.send_task, 'hello', args=args, chain=[Signature('hello')])
                    result = future.result()
                    while not executor.submit(is_ready, result).result():
                        time.sleep(0.001)
                else:
                    result = app.send_task('hello', args=args, chain=[Signature('hello')])
                assert result.get()
            gc.collect()
            get_mem_usage()
