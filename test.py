import time
import ctypes


def calculate_theoretical_cps(delay, interval):
    click_time = delay + interval
    clicks_per_second = 1 / click_time
    return clicks_per_second


def click(button=0, delay=0.001):
    ctypes.windll.user32.mouse_event(0, 0, 0, 0, 0)  # down
    time.sleep(delay)
    ctypes.windll.user32.mouse_event(0, 0, 0, 0, 0)  # up


def calculate_practical_cps(delay, interval, duration):
    total_clicks = 0
    start_time = time.perf_counter()

    while time.perf_counter() - start_time < duration:
        click(0, delay)
        time.sleep(interval)
        total_clicks += 1

    clicks_per_second = total_clicks / duration
    return clicks_per_second


# cps = calculate_practical_cps(0.01, 0.01, 1)
# print(f"Количество кликов в секунду: {cps:.2f}")

