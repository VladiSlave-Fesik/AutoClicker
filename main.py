import tkinter as tk
import time
import ctypes
import threading
import keyboard


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


def click(button=0, delay=0.001):
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][0], 0, 0, 0, 0)  # down
    time.sleep(delay)
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][1], 0, 0, 0, 0)  # up


def calculate_click_rate(delay, frequency):
    interval = 1 / frequency
    click_time = round(delay + interval, 3)
    click_rate = round(1 / click_time, 3)
    return click_time, click_rate


def interval_func(freq, delay):
    """Formula for calculating interval in autoclicker function"""
    return 1 / freq - delay


class AutoClicker(threading.Thread):
    def __init__(self, button=0, delay=0.001, frequence=10):
        super().__init__()
        self.button = button
        self.delay = delay
        self.frequence = frequence
        self.interval = interval_func(self.frequence, self.delay)

        if self.interval < 0:
            print('You need to either reduce the frequency or delay, interval will default = 0')
            self.interval = 0

        self.running = False

    def run(self):
        self.running = True
        while self.running:
            click(self.button, self.delay)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def start(self):
        if not self.running:
            super().start()

    def update_self(self, button=0, delay=0.001, frequence=10):
        self.button = button
        self.delay = delay
        self.frequence = frequence
        self.interval = interval_func(self.frequence, self.delay)

        if self.interval < 0:
            print('You need to either reduce the frequency or delay, interval will default = 0')
            self.interval = 0


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title()

        self.x_size = 300
        self.y_size = 300
        self.window.geometry(f'{self.x_size}x{self.y_size}')
        self.window.title('AutoClicker')
        self.window.iconbitmap(default='transparent.ico')

        self.autoclicker = AutoClicker()

        self.hotkey_button = tk.Button(width=8, height=2, command=self.get_key, text='Press key')
        self.hotkey_button.grid()
        self.label = tk.Label(self.window, text='')
        self.label.grid()
        # self.hotkey = keyboard.add_hotkey('a', self.toggle_autoclicker)

        self.window.mainloop()

    def toggle_autoclicker(self):
        if self.autoclicker.running:
            self.autoclicker.stop()
            self.button.config(text='Start')
        else:
            self.autoclicker.start()
            self.button.config(text='Stop')

    def get_key(self):
        self.hotkey_button.config(text='Waiting for input...', state='disabled')
        self.window.bind('<Key>', self.show_key)

    def show_key(self, event):
        self.label.config(text='Current Hotkey: ' + event.keysym)
        self.hotkey_button.config(text='Press key', state='normal')
        self.window.unbind('<Key>')


app = App()
