import time
import threading


def funA():
    print("funA started")
    t = threading.Thread(target=funB)
    t.start()
    print("funA returned")


def funB():
    print("funB started")
    time.sleep(10)
    print("funB completed")


if __name__ == "__main__":
    funA()
    print("Main thread continues...")
    time.sleep(11)
