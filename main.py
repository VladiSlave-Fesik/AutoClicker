import tkinter as tk
import time
import ctypes
import threading
import keyboard
import configparser
from textwrap import dedent, indent

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

MOUSE_BUTTONS = {
    0: (MOUSE_EVENT_LEFTDOWN, MOUSE_EVENT_LEFTUP),
    1: (MOUSE_EVENT_RIGHTDOWN, MOUSE_EVENT_RIGHTUP),
    2: (MOUSE_EVENT_MIDDLEDOWN, MOUSE_EVENT_MIDDLEUP)
}

click_actions = {
    0: "Left click",
    1: "Right click",
    2: "Middle click"
}

actions_click = {
    "Left click": 0,
    "Right click": 1,
    "Middle click": 2
}


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
    standard_autoclicker_settings = {
        'hotkey_key': 'F6',
        'delay': 0.001,
        'frequency': 10,
        'button': 0,
    }
    standard_autoclicker_settings_values = standard_autoclicker_settings.values()

    def __init__(self):
        self.window = tk.Tk()
        self.window.title()

        self.x_size = 300
        self.y_size = 300
        self.window.geometry(f'{self.x_size}x{self.y_size}')
        self.window.title('AutoClicker')
        self.window.iconbitmap(default='transparent.ico')
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)

        # getting config
        self.config_name = 'config.ini'
        self.hotkey_key, self.delay, self.frequency, self.button = self.load_config()

        print(f'''From [{self.config_name}] such values were loaded:\n{self.values_str(4)}\n''')

        self.autoclicker = AutoClicker(button=self.button, delay=self.delay, frequence=self.frequency)

        self.hotkey_button = tk.Button(width=8, height=2, command=self.get_key, text='Press key')
        self.hotkey_button.grid()

        self.hotkey = keyboard.add_hotkey(self.hotkey_key, self.toggle_autoclicker)
        self.current_hotkey_label = tk.Label(self.window, text=f'Current Hotkey: {self.hotkey_key}')
        self.current_hotkey_label.grid()

        self.delay_input = tk.Entry()
        self.delay_input.insert(0, str(self.delay))
        self.delay_input.grid()

        self.frequency_input = tk.Entry()
        self.frequency_input.insert(0, str(self.frequency))
        self.frequency_input.grid()

        self.current_button_label = tk.Label(self.window, text=f'Current click: {click_actions.get(self.button, "")}')
        self.current_button_label.grid()

        self.click_button_input = tk.Entry()
        self.click_button_input.insert(0, str(self.button))
        self.click_button_input.grid()

        self.click_button_input.bind("<KeyRelease>", self.update_current_button_label)
        self.click_button_input.grid()

        self.window.mainloop()

    def toggle_autoclicker(self):
        if self.autoclicker.running:
            self.autoclicker.stop()
        else:
            if not self.autoclicker.running:
                print(f'Run with:\n{self.values_str(4)}')
                self.autoclicker = AutoClicker(button=self.button, delay=float(self.delay_input.get()),
                                               frequence=self.frequency)
                self.autoclicker.start()

    def get_key(self):
        self.hotkey_button.config(text='Waiting for input...', state='disabled')
        self.window.bind('<Key>', self.show_key)

    def show_key(self, event):
        pressed_key = event.keysym
        if pressed_key != 'Escape':
            self.current_hotkey_label.config(text='Current Hotkey: ' + pressed_key)
            self.hotkey_button.config(text='Press key', state='normal')
            self.window.unbind('<Key>')

            keyboard.remove_hotkey(self.hotkey_key)
            self.hotkey_key = pressed_key
            self.hotkey = keyboard.add_hotkey(event.keysym, self.toggle_autoclicker)
        else:
            self.hotkey_button.config(text='Press key', state='normal')

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

        return App.standard_autoclicker_settings_values

    def update_current_button_label(self, event):
        try:
            button = int(self.click_button_input.get())
            self.button = button
            self.current_button_label.config(text=f'Current click: {click_actions.get(button, "")}')
        except ValueError:
            pass

    def set_new_values(self):
        # self.hotkey_key =
        # self.button =
        self.delay = float(self.delay_input.get())
        self.frequency = int(self.frequency_input.get())

    def values_str(self, space_nums=0):
        _ = f'{self.hotkey_key=}\n{self.delay=}\n{self.frequency=}\n{self.button=}'
        _ = indent(_, ' '*space_nums)
        return _

    def on_closing(self):
        self.set_new_values()
        print('The following values are saved in the config:')
        print(self.values_str(4)+'\n')
        self.write_config(hotkey=self.hotkey_key, delay=self.delay, frequency=self.frequency, button=self.button)
        # self.window.destroy()


if __name__ == '__main__':
    app = App()
