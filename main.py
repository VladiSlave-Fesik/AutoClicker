import ctypes
import time
import tkinter as tk
import threading


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("union", ctypes.POINTER(ctypes.c_ulonglong))]


MOUSE_EVENT_MOVE = 0x0001
MOUSE_EVENT_LEFTDOWN = 0x0002
MOUSE_EVENT_LEFTUP = 0x0004
MOUSE_EVENT_RIGHTDOWN = 0x0008
MOUSE_EVENT_RIGHTUP = 0x0010
MOUSE_EVENT_MIDDLEDOWN = 0x0020
MOUSE_EVENT_MIDDLEUP = 0x0040
MOUSE_EVENT_WHEEL = 0x0800
MOUSE_EVENT_XDOWN = 0x0080
MOUSE_EVENT_XUP = 0x0100

MOUSE_BUTTONS = {0: (MOUSE_EVENT_LEFTDOWN, MOUSE_EVENT_LEFTUP),
                 1: (MOUSE_EVENT_RIGHTDOWN, MOUSE_EVENT_RIGHTUP),
                 2: (MOUSE_EVENT_LEFTDOWN, MOUSE_EVENT_LEFTUP)}


def click(button=0, delay=0):
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][0], 0, 0, 0, 0)  # down
    time.sleep(delay)
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][1], 0, 0, 0, 0)  # up


# click(0)

def clicker(button=0, delay=0, frequency=1):
    global click_bool

    print(42)
    if frequency > 0:
        interval = 1 / frequency
    else:
        interval = 0
    while click_bool:
        print(4242)
        click(button=button, delay=delay)
        time.sleep(interval)


click_bool = True
class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title()

        self.x_size = 300
        self.y_size = 300
        self.window.geometry(f'{self.x_size}x{self.y_size}')
        self.window.title('AutoClicker')
        self.window.iconbitmap(default='transparent.ico')

        self.button = tk.Button(height=2, width=7, command=...)
        self.button.pack()

        self.window.mainloop()


th = threading.Thread(target=clicker)
th.start()

while True:
    time.sleep(0.1)
    print('yes')

# app = App()
