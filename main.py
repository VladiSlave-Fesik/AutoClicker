import tkinter as tk
from tkinter import ttk
import time
import ctypes
import threading
import keyboard
import configparser
from textwrap import dedent, indent
from PIL import Image, ImageTk

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


class AutoClicker(threading.Thread):
    def __init__(self, button=0, delay=0.001, interval=0):
        super().__init__()
        self.button = button
        self.delay = delay
        self.interval = interval

        if self.interval < 0:
            self.interval = 0

        if self.delay < 0:
            self.delay = 0

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

    def update_self(self, button=0, delay=0.001, interval=0):
        self.button = button
        self.delay = delay
        self.interval = interval

        if self.interval <= 0:
            self.interval = 0

        if self.delay <= 0:
            self.delay = 0


class TimeInput(tk.Frame):
    def __init__(self, master=None, time_=None, **kwargs):
        super().__init__(master, **kwargs)
        self.hour = tk.StringVar()
        self.minute = tk.StringVar()
        self.second = tk.StringVar()

        if not time_:
            self.hour.set("00")
            self.minute.set("00")
            self.second.set("00")
        else:
            self.hour.set(time_[0])
            self.minute.set(time_[1])
            self.second.set(time_[2])

        self.hour_entry = tk.Entry(self, textvariable=self.hour, width=2, justify='center')
        self.minute_entry = tk.Entry(self, textvariable=self.minute, width=2, justify='center')
        self.second_entry = tk.Entry(self, textvariable=self.second, width=2, justify='center')

        self.hour_entry.pack(side=tk.LEFT)
        tk.Label(self, text=':').pack(side=tk.LEFT)
        self.minute_entry.pack(side=tk.LEFT)
        tk.Label(self, text=':').pack(side=tk.LEFT)
        self.second_entry.pack(side=tk.LEFT)

    def get_time(self):
        hour = self.hour.get()
        minute = self.minute.get()
        second = self.second.get()

        try:
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return f"{hour:02d}:{minute:02d}:{second:02d}"
        except ValueError:
            pass

        return None


class App:
    standard_autoclicker_settings = {
        'hotkey_key': 'F6',
        'delay': 0.001,
        'interval': 0,
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

        # load images
        self.icon_name = 'data/images/transparent.ico'
        self.icon_save_button = 'data/images/save.png'

        self.icon_save_button_img = Image.open(self.icon_save_button).resize((50, 50))
        self.icon_save_button_img = ImageTk.PhotoImage(self.icon_save_button_img)

        self.icon_key_button = 'data/images/key_0.png'
        self.icon_key_button_img = Image.open(self.icon_key_button).resize((50, 50))
        self.icon_key_button_img = ImageTk.PhotoImage(self.icon_key_button_img)

        self.window.iconbitmap(default=self.icon_name)
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.window.bind("<Button-1>", self.handle_click)

        # getting config
        self.config_name = 'data/configs/config.ini'
        self.hotkey_key, self.delay, self.interval, self.button = self.load_config()

        print(f'''From [{self.config_name}] such values were loaded:\n{self.values_str(4)}\n''')

        self.autoclicker = AutoClicker(button=self.button, delay=self.delay, interval=self.interval)

        self.hotkey_button = tk.Button(command=self.get_key, image=self.icon_key_button_img, bd=0, highlightthickness=0)
        self.hotkey_button.grid()

        self.hotkey = keyboard.add_hotkey(self.hotkey_key, self.toggle_autoclicker)
        self.current_hotkey_label = tk.Label(self.window, text=f'Current Hotkey: {self.hotkey_key}')
        self.current_hotkey_label.grid()

        self.delay_input = tk.Entry()
        self.delay_input.insert(0, str(self.delay))
        self.delay_input.grid()

        self.time_input = TimeInput(self.window, time_=self.format_time(self.interval).split(':'))
        self.time_input.grid()

        self.click_selection = ttk.Combobox(values=list(actions_click.keys()), state='readonly')
        self.click_selection.set(click_actions[self.button])
        self.click_selection.grid()

        self.button_save_config = tk.Button(command=self.save_config_button, image=self.icon_save_button_img, bd=0, highlightthickness=0)
        self.button_save_config.grid()

        self.window.mainloop()

    def toggle_autoclicker(self):
        self.update_values()
        if self.autoclicker.running:
            self.autoclicker.stop()
            print('Stop')
        else:
            if not self.autoclicker.running:
                print(f'Run with:\n{self.values_str(4)}')
                self.autoclicker = AutoClicker(button=self.button, delay=float(self.delay_input.get()),
                                               interval=self.interval)
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

    def write_config(self, hotkey, delay, interval, button):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'hotkey_key': hotkey,
            'delay': str(delay),
            'interval': str(interval),
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
            delay = settings.getfloat('delay', 0.001)
            interval = settings.getint('interval', 0)
            button = settings.getint('button', 0)
            return hotkey_key, delay, interval, button

        return App.standard_autoclicker_settings_values

    def update_values(self):
        # self.hotkey_key =
        self.button = actions_click[self.click_selection.get()]
        self.delay = float(self.delay_input.get())
        self.interval = self.get_time()

    def values_str(self, space_nums=0):
        _ = f'{self.hotkey_key=}\n{self.delay=}\n{self.interval=}\n{self.button=}'
        _ = indent(_, ' ' * space_nums)
        return _

    def on_closing(self):
        self.window.destroy()

    def get_time(self):
        time_ = self.time_input.get_time()
        return self.time_to_seconds(time_)

    @staticmethod
    def time_to_seconds(time_: str):
        h, m, s = map(int, time_.split(':'))
        seconds = (h * 3600) + (m * 60) + s
        return seconds

    @staticmethod
    def format_time(seconds: int):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def save_config_button(self):
        self.update_values()
        print('The following values are saved in the config:')
        print(self.values_str(4) + '\n')
        self.write_config(hotkey=self.hotkey_key, delay=self.delay, interval=self.interval, button=self.button)

    def handle_click(self, event):
        if event.widget == self.window:
            self.window.focus_set()


if __name__ == '__main__':
    app = App()
