import configparser
import ctypes
import os
import threading
import time
from textwrap import indent
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import keyboard

MOUSE_EVENT_NOTHING = 0
MOUSE_EVENT_LEFTDOWN = 0x0002
MOUSE_EVENT_LEFTUP = 0x0004
MOUSE_EVENT_RIGHTDOWN = 0x0008
MOUSE_EVENT_RIGHTUP = 0x0010
MOUSE_EVENT_MIDDLEDOWN = 0x0020
MOUSE_EVENT_MIDDLEUP = 0x0040


MOUSE_BUTTONS = {
    0: (MOUSE_EVENT_NOTHING, MOUSE_EVENT_NOTHING),
    1: (MOUSE_EVENT_LEFTDOWN, MOUSE_EVENT_LEFTUP),
    2: (MOUSE_EVENT_RIGHTDOWN, MOUSE_EVENT_RIGHTUP),
    3: (MOUSE_EVENT_MIDDLEDOWN, MOUSE_EVENT_MIDDLEUP)
}

click_actions = {
    1: 'Left click',
    2: 'Right click',
    3: 'Middle click',
}

actions_click = {v: k for k, v in click_actions.items()}


def click(button=0, delay=0.001):
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][0], 0, 0, 0, 0)  # down
    skip_time(delay)
    ctypes.windll.user32.mouse_event(MOUSE_BUTTONS[button][1], 0, 0, 0, 0)  # up


def calculate_theoretical_cps(delay, interval):
    click_time = delay + interval
    if click_time == 0:
        return 'Infinity'
    clicks_per_second = 1 / click_time
    return clicks_per_second


def calculate_practical_cps(delay, interval, calculation_duration):
    total_clicks = 0
    start_time = time.perf_counter()

    while time.perf_counter() - start_time < calculation_duration:
        click(0, delay)
        skip_time(interval)
        total_clicks += 1

    clicks_per_second = total_clicks / calculation_duration
    return clicks_per_second


def skip_time(seconds):
    start_time = time.perf_counter()
    target_time = start_time + seconds

    while time.perf_counter() < target_time:
        pass


class CPSCalculationThread(threading.Thread):
    def __init__(self, delay, interval, calculation_duration, callback):
        super().__init__()
        self.delay = delay
        self.interval = interval
        self.calculation_duration = calculation_duration
        self.callback = callback

    def run(self):
        total_clicks = 0
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < self.calculation_duration:
            # Выполнение расчетов CPS
            click(0, self.delay)
            skip_time(self.interval)
            total_clicks += 1

        clicks_per_second = total_clicks / self.calculation_duration

        # Вызов обратного вызова с результатом расчетов
        self.callback(clicks_per_second)


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
            skip_time(self.interval)

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
        self.millisecond = tk.StringVar()

        if not time_:
            self.hour.set("00")
            self.minute.set("00")
            self.second.set("00")
            self.millisecond.set("000")
        else:
            self.hour.set(time_[0])
            self.minute.set(time_[1])
            self.second.set(time_[2])
            self.millisecond.set(time_[3])

        self.hour_entry = tk.Entry(self, textvariable=self.hour, width=5, justify='center', bd=1,
                                   highlightthickness=0)
        self.minute_entry = tk.Entry(self, textvariable=self.minute, width=5, justify='center', bd=1,
                                     highlightthickness=0)
        self.second_entry = tk.Entry(self, textvariable=self.second, width=5, justify='center', bd=1,
                                     highlightthickness=0)
        self.millisecond_entry = tk.Entry(self, textvariable=self.millisecond, width=5, justify='center', bd=1,
                                          highlightthickness=0)

        self.hour_entry.pack(side=tk.LEFT)
        tk.Label(self, text=':').pack(side=tk.LEFT)
        self.minute_entry.pack(side=tk.LEFT)
        tk.Label(self, text=':').pack(side=tk.LEFT)
        self.second_entry.pack(side=tk.LEFT)
        tk.Label(self, text=':').pack(side=tk.LEFT)
        self.millisecond_entry.pack(side=tk.LEFT)

    def get_time(self):
        hour = self.hour.get()
        minute = self.minute.get()
        second = self.second.get()
        millisecond = self.millisecond.get()

        try:
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            millisecond = self.format_milliseconds(millisecond)
            return f'{hour}:{minute}:{second}:{millisecond}'
        except ValueError:
            pass

        return None

    def update_time(self, time_):
        self.hour.set(time_[0])
        self.minute.set(time_[1])
        self.second.set(time_[2])
        self.millisecond.set(time_[3])

    @staticmethod
    def format_milliseconds(milliseconds):
        if len(milliseconds) > 3:
            milliseconds = milliseconds[:3] + '.' + milliseconds[3:]
        elif len(milliseconds) < 3:
            milliseconds = milliseconds.zfill(3)
        return milliseconds


class App:
    standard_autoclicker_settings = {
        'hotkey_key': 'F6',
        'delay': 0.001,
        'interval': 0,
        'button': 1,
    }
    standard_autoclicker_settings_values = standard_autoclicker_settings.values()

    def __init__(self):
        self.window = tk.Tk()
        self.window.title()

        self.x_size = 250
        self.y_size = 150
        self.window.geometry(f'{self.x_size}x{self.y_size}')
        self.window.title('AutoClicker')

        # flag
        self.is_waiting_for_key = False

        # folders
        self.folder_data = 'data'
        self.folder_configs = os.path.join(self.folder_data, 'configs')
        self.folder_images = os.path.join(self.folder_data, 'images')

        # load images
        self.icon_name = os.path.join(self.folder_images, 'autoclicker.ico')
        self.icon_key_button = os.path.join(self.folder_images, 'key.png')

        self.icon_key_button_img = tk.PhotoImage(file=self.icon_key_button)

        self.window.iconbitmap(default=self.icon_name)
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.window.resizable(width=False, height=False)
        self.window.bind("<Button-1>", self.handle_click)

        # getting config
        self.standard_config_name = os.path.join(self.folder_configs, 'config.ini')
        self.config_name = self.standard_config_name

        self.hotkey_key, self.delay, self.interval, self.button = self.load_config()
        self.calculation_duration = 1

        self.autoclicker = AutoClicker(button=self.button, delay=self.delay, interval=self.interval)

        self.hotkey_button = tk.Button(command=self.get_key, image=self.icon_key_button_img, bd=0, highlightthickness=0)
        self.hotkey_button.grid(row=0, column=0)

        self.hotkey = keyboard.add_hotkey(self.hotkey_key, self.toggle_autoclicker)
        self.current_hotkey_label = tk.Label(self.window, text=f'Current Hotkey: {self.hotkey_key}')
        self.current_hotkey_label.grid(row=0, column=1)

        self.delay_label = tk.Label(self.window, text='Delay:')
        self.delay_label.grid(row=1, column=0)
        self.delay_input = tk.Entry(width=15)
        self.delay_input.insert(0, str(self.delay))
        self.delay_input.grid(row=1, column=1)

        self.time_label = tk.Label(self.window, text='Interval:\n(h:m:s:ms)')
        self.time_label.grid(row=2, column=0)
        self.time_input = TimeInput(self.window, time_=self.format_time(self.interval).split(':'))
        self.time_input.grid(row=2, column=1)

        self.click_label = tk.Label(self.window, text='Click Action:')
        self.click_label.grid(row=3, column=0)
        self.click_selection = ttk.Combobox(values=list(actions_click.keys()), state='readonly', width=10)
        self.click_selection.set(click_actions[self.button])
        self.click_selection.grid(row=3, column=1)

        # set menu bar
        self.menu_bar = tk.Menu()

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.config_menu.add_command(label='Open config', command=self.open_config_dialog)
        self.config_menu.add_command(label='Save config', command=self.save_config)
        self.config_menu.add_command(label='Save config as', command=self.save_config_as)

        self.calculate_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.calculate_menu.add_command(label='Calculate theoretical cps',
                                        command=self.calculate_theoretical_cps)
        self.calculate_menu.add_command(label='Calculate practical cps',
                                        command=self.calculate_practical_cps)

        self.menu_bar.add_cascade(label='Configuration', menu=self.config_menu)
        self.menu_bar.add_cascade(label='Calculations', menu=self.calculate_menu)

        self.window.config(menu=self.menu_bar)

        self.window.mainloop()

    def toggle_autoclicker(self):
        self.update_values()
        if self.autoclicker.running:
            self.autoclicker.stop()
            print('Stop autoclicker\n')
        else:
            if not self.autoclicker.running and not self.is_waiting_for_key:
                print(f'Run autoclicker with:\n{self.values_str(4)}\n')
                self.autoclicker = AutoClicker(button=self.button, delay=self.delay,
                                               interval=self.interval)
                self.autoclicker.start()

    def get_key(self):
        if not self.is_waiting_for_key:
            self.hotkey_button.config(state='disabled')
            self.current_hotkey_label.config(text='Waiting for input...\n (Escape to cancel)')
            self.window.bind('<Key>', self.show_key)
            self.is_waiting_for_key = True

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
            self.current_hotkey_label.config(text='Current Hotkey: ' + self.hotkey_key)
        self.is_waiting_for_key = False


    def write_config(self, hotkey, delay, interval, button, config_=None):
        if config_ is None:
            config_ = self.config_name

        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'hotkey_key': hotkey,
            'delay': str(delay),
            'interval': str(interval),
            'button': str(button)
        }

        with open(config_, 'w') as config_file:
            config.write(config_file)

        print(f'''The following values are saved in the config [{config_}]:\n{self.values_str(space_nums=4,
                                                                                       hotkey_key=hotkey,
                                                                                       delay=delay,
                                                                                       interval=interval,
                                                                                       button=button)}\n''')

    def load_config(self, config_=None):
        if config_ is None:
            config_ = self.config_name

        defaul_config = App.standard_autoclicker_settings

        config = configparser.ConfigParser()
        config.read(config_)

        if 'SETTINGS' in config:
            settings = config['SETTINGS']
            hotkey_key = settings.get('hotkey_key', defaul_config['hotkey_key'])
            delay = settings.getfloat('delay', defaul_config['delay'])
            interval = settings.getfloat('interval', defaul_config['interval'])
            button = settings.getint('button', defaul_config['button'])
            print(f'''From [{config_}] such values were loaded:\n{self.values_str(space_nums=4,
                                                                                           hotkey_key=hotkey_key,
                                                                                           delay=delay,
                                                                                           interval=interval,
                                                                                           button=button)}\n''')
            return hotkey_key, delay, interval, button

        print('Standard values are loaded')
        return App.standard_autoclicker_settings_values

    def update_values(self):
        # self.hotkey_key =
        self.button = actions_click[self.click_selection.get()]
        self.delay = float(self.delay_input.get())
        self.interval = self.get_time()

    def values_str(self, space_nums=0, hotkey_key=None, delay=None, interval=None, button=None):
        hotkey_key = self.hotkey_key if hotkey_key is None else hotkey_key
        delay = self.delay if delay is None else delay
        interval = self.interval if interval is None else interval
        button = self.button if button is None else button

        _ = f'{hotkey_key=}\n{delay=}\n{interval=}\n{button=}'
        _ = indent(_, ' ' * space_nums)
        return _

    def on_closing(self):
        self.window.destroy()

    def get_time(self):
        time_ = self.time_input.get_time()
        return self.time_to_seconds(time_)

    @staticmethod
    def time_to_seconds(time_: str):
        h, m, s = map(int, time_.split(':')[:-1])
        ms = float(time_.split(':')[-1])
        seconds = (h * 3600) + (m * 60) + s + (ms / 1000)
        return seconds

    @staticmethod
    def format_time(seconds: int):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        return f"{hours}:{minutes}:{seconds}:{milliseconds}"

    def save_config(self):
        self.update_values()
        self.write_config(hotkey=self.hotkey_key, delay=self.delay, interval=self.interval, button=self.button)

    def save_config_as(self):
        file_path = filedialog.asksaveasfilename(
            initialdir=self.folder_configs,
            title='Save As',
            filetypes=(('INI files', '*.ini'), ('All files', '*.*')),
        )
        if file_path:
            if not file_path.endswith('.ini'):
                file_path += '.ini'
            print('Selected file path:', file_path)

            self.update_values()
            self.write_config(hotkey=self.hotkey_key, delay=self.delay, interval=self.interval,
                              button=self.button, config_=file_path)

    def handle_click(self, event):
        if event.widget == self.window:
            self.window.focus_set()

    def open_config_dialog(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilenames(initialdir=self.folder_configs)
        if file_path:
            file_path, = file_path
            print('Selected file path:', file_path)
            keyboard.remove_hotkey(self.hotkey_key)

            self.config_name = file_path
            self.hotkey_key, self.delay, self.interval, self.button = self.load_config()

            self.autoclicker = AutoClicker(button=self.button, delay=self.delay, interval=self.interval)
            self.current_hotkey_label.config(text=f'Current Hotkey: {self.hotkey_key}')
            self.delay_input.delete(0, 'end')
            self.delay_input.insert(0, str(self.delay))
            self.time_input.update_time(self.format_time(self.interval).split(':'))
            self.click_selection.set(click_actions[self.button])

            self.hotkey = keyboard.add_hotkey(self.hotkey_key, self.toggle_autoclicker)

    def calculate_practical_cps(self):
        self.update_values()

        def handle_result(cps_result):
            print(f'Practical clicks per second ~ {cps_result:.2f} with:\n\t{self.delay=}'
                  f'\n\t{self.interval=}\n\t{self.calculation_duration=}\n')

            message = f'Practical clicks per second ~ {cps_result:.2f}'
            messagebox.showinfo("CPS Calculation Result", message)

        cps_thread = CPSCalculationThread(delay=self.delay, interval=self.interval,
                                          calculation_duration=self.calculation_duration, callback=handle_result)
        cps_thread.start()

    def calculate_theoretical_cps(self):
        self.update_values()
        cps_result = calculate_theoretical_cps(delay=self.delay, interval=self.interval)
        print(f'Theoretical clicks per second: {cps_result:.2f} with:\n\t{self.delay=}\n\t{self.interval=}\n')

        message = f'Theoretical clicks per second: {cps_result:.2f}'
        messagebox.showinfo('CPS Calculation Result', message)


if __name__ == '__main__':
    app = App()
