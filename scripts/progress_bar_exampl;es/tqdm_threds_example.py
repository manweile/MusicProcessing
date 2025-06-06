import threading
import time
from tqdm import tqdm
import queue


def worker(q, progress_bar):
    while True:
        task = q.get()
        if task is None:
            break
        time.sleep(0.1)  # Simulate work
        progress_bar.update(1)
        q.task_done()


if __name__ == "__main__":
    num_tasks = 100
    num_threads = 4

    task_queue = queue.Queue()
    for _ in range(num_tasks):
        task_queue.put(1)

    progress_bar = tqdm(total=num_tasks, desc="Processing tasks")

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(task_queue, progress_bar))
        thread.start()
        threads.append(thread)

    # Block until all tasks are done
    task_queue.join()

    # Stop workers
    for _ in range(num_threads):
        task_queue.put(None)
    for thread in threads:
        thread.join()

    progress_bar.close()
