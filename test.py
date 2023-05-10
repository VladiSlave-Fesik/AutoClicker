import tkinter as tk
import time
import ctypes
import threading
import keyboard


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


class AutoClicker(threading.Thread):
    def __init__(self, button=0, delay=0.1, frequence=10):
        super().__init__()
        self.button = button
        self.delay = delay
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            click(self.button, self.delay)

    def stop(self):
        self.running = False

    def start(self):
        if not self.running:
            super().start()


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title()

        self.x_size = 300
        self.y_size = 300
        self.window.geometry(f'{self.x_size}x{self.y_size}')
        self.window.title('AutoClicker')
        self.window.iconbitmap(default='transparent.ico')

        self.canvas = tk.Canvas(self.window, width=self.x_size, height=self.y_size)
        self.canvas.pack()
        self.canvas.bind('<Motion>', self._is_cursor_inside)
        self.canvas.place(x=0, y=0)

        self.autoclicker = AutoClicker()

        self.button = tk.Button(height=2, width=7, command=self.toggle_autoclicker)
        self.button.pack()

        self.hot = keyboard.add_hotkey('a', self.toggle_autoclicker)

        self.window.mainloop()

    def toggle_autoclicker(self):
        if self.autoclicker.running:
            self.autoclicker.stop()
            self.button.config(text='Start')
        else:
            self.autoclicker.start()
            self.button.config(text='Stop')

    def _is_cursor_inside(self, event):
        x = self.window.winfo_pointerx() - self.window.winfo_rootx()
        y = self.window.winfo_pointery() - self.window.winfo_rooty()

        if 0 <= x <= self.window.winfo_width() and 0 <= y <= self.window.winfo_height():
            print('in')
        else:
            print('not in')




app = App()


