import os
import json
import time
import queue
import threading
import logging
import socket

import redis  # lightweight task queue via redis lists

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
TASK_QUEUE = os.getenv('TASK_QUEUE', 'mea:tasks')
RESULT_QUEUE = os.getenv('RESULT_QUEUE', 'mea:results')
WORKER_NAME = os.getenv('WORKER_NAME', socket.gethostname())
CONCURRENCY = int(os.getenv('WORKER_CONCURRENCY', '1'))


def do_work(task: dict) -> dict:
    """Procesa una tarea mínima (placeholder). Mantener CPU bajo en hardware débil."""
    # ejemplo: pequeño procesamiento de texto
    text = task.get('text', '')
    tokens = text.lower().split()
    unique = sorted(set(tokens))
    # simular trabajo ligero
    time.sleep(min(len(tokens) * 0.005, 0.2))
    return {
        'worker': WORKER_NAME,
        'unique_tokens': unique,
        'count': len(tokens)
    }


def worker_loop(client: redis.Redis, thread_id: int):
    logger.info("Worker thread %s started", thread_id)
    while True:
        try:
            item = client.blpop(TASK_QUEUE, timeout=5)
            if item is None:
                continue
            _, payload = item
            task = json.loads(payload)
            result = do_work(task)
            client.rpush(RESULT_QUEUE, json.dumps({
                'task_id': task.get('id'),
                'result': result,
                'ts': time.time()
            }))
        except Exception as exc:
            logger.exception("Error procesando tarea: %s", exc)


def main():
    client = redis.from_url(REDIS_URL, decode_responses=False)
    logger.info("Worker %s conectado a %s; cola=%s", WORKER_NAME, REDIS_URL, TASK_QUEUE)
    threads = []
    for i in range(CONCURRENCY):
        t = threading.Thread(target=worker_loop, args=(client, i), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()

