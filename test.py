import keyboard
import time
from pynput.mouse import Listener
import sys
import ctypes
import random
from ctypes import wintypes
import re

MOUSE_EVENT_NOTHING = 0
MOUSE_EVENT_LEFTDOWN = 0x0002
MOUSE_EVENT_LEFTUP = 0x0004
MOUSE_EVENT_RIGHTDOWN = 0x0008
MOUSE_EVENT_RIGHTUP = 0x0010
MOUSE_EVENT_MIDDLEDOWN = 0x0020
MOUSE_EVENT_MIDDLEUP = 0x0040

MOUSE_EVENT_XDOWN = 0x0080
MOUSE_EVENT_XUP = 0x0100

MOUSE_EVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

MOUSE_EVENTS = {
    0: ((MOUSE_EVENT_NOTHING, 0, 0, 0, 0), (MOUSE_EVENT_NOTHING, 0, 0, 0, 0)),
    1: ((MOUSE_EVENT_LEFTDOWN, 0, 0, 0, 0), (MOUSE_EVENT_LEFTUP, 0, 0, 0, 0)),
    2: ((MOUSE_EVENT_RIGHTDOWN, 0, 0, 0, 0), (MOUSE_EVENT_RIGHTUP, 0, 0, 0, 0)),
    3: ((MOUSE_EVENT_MIDDLEDOWN, 0, 0, 0, 0), (MOUSE_EVENT_MIDDLEUP, 0, 0, 0, 0)),
    4: ((MOUSE_EVENT_XDOWN, 0, 0, 1, 0), (MOUSE_EVENT_XUP, 0, 0, 1, 0)),
    5: ((MOUSE_EVENT_XDOWN, 0, 0, 2, 0), (MOUSE_EVENT_XUP, 0, 0, 2, 0))
}


def on_click(x: int, y: int, button, pressed: bool):
    global last_action
    action_time = time.time() - last_action
    last_action = time.time()
    button = str(button)
    button = 1 if button.endswith('left') else 2 if button.endswith('right') else 3 if button.endswith(
        'middle') else 4 if button.endswith('x1') else 5 if button.endswith('x2') else button
    if pressed:
        press_or_release = 'press'
    else:
        press_or_release = 'release'
    action = f'skip_time({action_time})\n{press_or_release}({button=})'
    print(action)
    actions.append(action)


def on_move(x, y):
    global last_action
    action = f'skip_time({time.time() - last_action})\nmove_to({x}, {y})'
    print(action)
    last_action = time.time()
    # print(action)
    actions.append(action)


def on_scroll(*args):
    global last_action
    action = f'skip_time({time.time() - last_action})\nscroll({args[-1]})'
    last_action = time.time()
    print(action)
    actions.append(action)


def start_listener():
    with Listener(on_click=on_click, on_move=on_move) as listener:
        listener.join()


def stop_listener():
    listener.stop()


def press(button=0, delay=0.001):
    ctypes.windll.user32.mouse_event(*MOUSE_EVENTS[button][0])  # down
    skip_time(delay)


def release(button=0, delay=0.001):
    ctypes.windll.user32.mouse_event(*MOUSE_EVENTS[button][1])  # up
    skip_time(delay)


def scroll(amount):
    MOUSEEVENTF_WHEEL = 0x0800
    WHEEL_DELTA = 120

    class MouseInput(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

    class Input(ctypes.Structure):
        class _INPUT(ctypes.Union):
            _fields_ = [("mi", MouseInput)]

        _fields_ = [("type", ctypes.c_ulong),
                    ("value", _INPUT)]

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, amount * WHEEL_DELTA, 0)


def move_to(end_x, end_y, duration=0):
    start_x, start_y = ctypes.wintypes.POINT(), ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(start_x))
    start_x, start_y = start_x.x, start_x.y

    steps = 100
    interval = duration / steps

    dx = (end_x - start_x) / steps
    dy = (end_y - start_y) / steps

    x = start_x
    y = start_y

    for _ in range(steps):
        x += dx
        y += dy

        ctypes.windll.user32.SetCursorPos(int(x), int(y))

        time.sleep(interval)

    ctypes.windll.user32.SetCursorPos(end_x, end_y)


def skip_time(seconds):
    start_time = time.perf_counter()
    target_time = start_time + seconds

    while time.perf_counter() < target_time:
        pass


def run_record():
    with open('record.txt', 'r') as file:
        for line in file.readlines():
            exec(line)


def compress_record(file_name):
    with open(file_name+'.txt', 'r') as original_file:
        text = original_file.readlines()

    with open(file_name + '_compress.txt', 'w') as new_file:
        for line in text:
            line = re.sub(r"press\(button=(\d+)\)", r"p(\1)", line)
            line = re.sub(r"skip_time\(([\d.]+)\)", lambda m: f"s({round(float(m.group(1)), 5)})", line)
            line = re.sub(r"release\(button=(\d+)\)", r"r(\1)", line)
            line = re.sub(r"move_to\(x=(\d+), y=(\d+)\)", r"m(\1, \2)", line)
            new_file.write(line)


mode = 3

if mode == 1:
    time.sleep(2)
    run_record()
elif mode == 2:
    actions = []
    last_action = time.time()
    keyboard.add_hotkey('ctrl+q', stop_listener)

    with Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move) as listener:
        listener.join()

    with open('record.txt', 'w') as file:
        file.write('\n'.join(actions))

elif mode == 3:
    compress_record('record')

print('\nEnd')
