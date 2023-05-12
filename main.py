import tkinter as tk
import time
import ctypes
import threading
import keyboard
import configparser
from textwrap import dedent

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
                 2: (MOUSE_EVENT_MIDDLEDOWN, MOUSE_EVENT_MIDDLEUP)}


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

        if self.interval <= 0:
            print('You need to either reduce the frequency or delay, interval will default = 0')
            self.interval = 0

        self.running = False

    def run(self):
        self.running = True
        while self.running:
            click(button=self.button, delay=self.delay)
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

        # getting config
        self.config_name = 'config.ini'
        self.hotkey_key, self.delay, self.frequency, self.button = self.load_config()
        print(dedent(f'''
    From [{self.config_name}] such values were loaded:
            {self.hotkey_key=}
            {self.delay=}
            {self.frequency=}
            {self.button=}'''.strip()))

        self.autoclicker = AutoClicker(button=self.button, delay=self.delay, frequence=self.frequency)

        self.hotkey_button = tk.Button(width=8, height=2, command=self.get_key, text='Press key')
        self.hotkey_button.grid()

        self.hotkey = keyboard.add_hotkey(self.hotkey_key, self.toggle_autoclicker)
        self.label = tk.Label(self.window, text=f'Current Hotkey: {self.hotkey_key}')
        self.label.grid()

        # self.hotkey = keyboard.add_hotkey('a', self.toggle_autoclicker)
        # keyboard.remove_hotkey('a')

        self.window.mainloop()

    def toggle_autoclicker(self):
        if self.autoclicker.running:
            self.autoclicker.stop()
        else:
            if not self.autoclicker.running:
                self.autoclicker = AutoClicker(button=self.button, delay=self.delay, frequence=self.frequency)
                self.autoclicker.start()

    def get_key(self):
        self.hotkey_button.config(text='Waiting for input...', state='disabled')
        self.window.bind('<Key>', self.show_key)

    def show_key(self, event):
        pressed_key = event.keysym
        self.label.config(text='Current Hotkey: ' + pressed_key)
        self.hotkey_button.config(text='Press key', state='normal')
        self.window.unbind('<Key>')

        self.hotkey_key = pressed_key
        self.hotkey = keyboard.add_hotkey(event.keysym, self.toggle_autoclicker)
        self.write_config(hotkey=self.hotkey_key, delay=self.delay, frequency=self.frequency, button=self.button)

    def write_config(self, hotkey, delay, frequency, button):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'hotkey_key': hotkey,
            'delay': str(delay),
            'frequency': str(frequency),
            'button': str(button)
        }

        with open(self.config_name, 'w') as config_file:
            config.write(config_file)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_name)

        if 'SETTINGS' in config:
            settings = config['SETTINGS']
            hotkey_key = settings.get('hotkey_key', 'F6')
            delay = settings.getfloat('delay', 0.1)
            frequency = settings.getint('frequency', 10)
            button = settings.getint('button', 0)
            return hotkey_key, delay, frequency, button

        return 'F6', 0.1, 10, 0


if __name__ == '__main__':
    app = App()




