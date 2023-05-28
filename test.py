import keyboard
import time
from pynput.mouse import Listener, Button, Controller
import sys
import ctypes
import random
from ctypes import wintypes


def on_press(x: int, y: int, button, pressed: bool):
    global start_time
    action_time = time.time() - start_time
    start_time = time.time()
    print(button, button.value)
    button = str(button)
    button = 1 if button.endswith('left') else 2 if button.endswith('right') else 3 if button.endswith(
        'middle') else button
    if pressed:
        press_or_release = 'pressed'
    else:
        press_or_release = 'release'
    action = f'sleep({action_time})\n{press_or_release}({x=}, {y=}, {button=})'
    print(action)
    actions.append(action)


class A:
    def __init__(self, value):
        self.value = value


def send_input(input_tuple):
    # Подготовка массива INPUT для передачи в SendInput
    inputs = (ctypes.c_ulong * len(input_tuple))()

    # Создание объектов INPUT с указанными значениями
    for i, (dwFlags, mouseData) in enumerate(input_tuple):
        inputs[i].type = ctypes.c_ulong(INPUT_MOUSE)
        inputs[i].mi.dwFlags = dwFlags
        inputs[i].mi.mouseData = mouseData

    # Вызов функции SendInput
    SendInput(len(input_tuple), inputs, ctypes.sizeof(INPUT))


actions = []
start_time = time.time()
mouse = Controller()
SendInput = ctypes.windll.user32.SendInput
# time.sleep(2)
b = (256, 128, 2)
a = A(b)


# ctypes.windll.user32.mouse_event(256, 0, 0, 0, 0)
# ctypes.windll.user32.mouse_event(128, 0, 0, 0, 0)

# with Listener(on_click=on_press) as listener:
#     listener.join()


def skip_time(seconds):
    start_time = time.perf_counter()
    target_time = start_time + seconds

    while time.perf_counter() < target_time:
        pass


def click(button, delay=0.001):
    ctypes.windll.user32.mouse_event(button[0], 0, 0, 0, 0)  # down
    skip_time(delay)
    ctypes.windll.user32.mouse_event(button[1], 0, 0, 0, 0)  # up


time.sleep(2)
# Константы для событий мыши
MOUSE_EVENT_XBUTTON1DOWN = 0x0080
MOUSE_EVENT_XBUTTON1UP = 0x0100

ctypes.windll.user32.mouse_event(0x0080, 0, 0, 2, 0)  # down

ctypes.windll.user32.mouse_event(0x0100, 0, 0, 2, 0)  # up

