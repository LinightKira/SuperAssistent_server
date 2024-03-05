import threading
import time
import asyncio


async def long_running_task(task_id):
    print(f"Task {task_id} started")
    await asyncio.sleep(5)  # 模拟一个耗时操作
    print(f"Task {task_id} finished")


async def start_tasks_async():
    tasks = []
    for i in range(3):
        task = asyncio.create_task(long_running_task(i))
        tasks.append(task)

    await asyncio.gather(*tasks)


def start_tasks():
    asyncio.run(start_tasks_async())


def main():
    print("Main thread started")

    # 在主线程中启动异步任务
    thread = threading.Thread(target=start_tasks)
    thread.start()
    thread.join()

    print("Main thread finished")


if __name__ == "__main__":
    main()
