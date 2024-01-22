import threading
import time
import io
import sys
import os

def func(text, output):
    while True:
        time.sleep(2)
        print(text, file=output)

def func2(text):
    while True:
        inp = input("Skriv något: ")
        print(inp)

if __name__=="__main__":
    text = "asdfghjklöqwertyuiopåzxcvbnm"
    text2 = "ba"

    cmd_output = io.StringIO()
    thr_output = io.StringIO()
    sys.stdout = cmd_output

    thread1 = threading.Thread(target = func, args = (text, thr_output))
    thread2 = threading.Thread(target = func2, args = (text2, ))

    thread1.start()
    thread2.start()

    os.system("clear")
    while True:
        cmd_output.seek(0)
        thr_output.seek(0)
        cmd_line = cmd_output.read()
        thr_line = thr_output.read()

        print("\033[0;0H" + thr_line + cmd_line + "\033[20;0H", file=sys.__stdout__)
