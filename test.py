import threading
import time
import tkinter as tk
from main import click

class CPSCalculationThread(threading.Thread):
    def __init__(self, delay, interval, duration, callback):
        super().__init__()
        self.delay = delay
        self.interval = interval
        self.duration = duration
        self.callback = callback

    def run(self):
        total_clicks = 0
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < self.duration:
            # Выполнение расчетов CPS
            click(0, self.delay)
            time.sleep(self.interval)
            total_clicks += 1

        clicks_per_second = total_clicks / self.duration

        # Вызов обратного вызова с результатом расчетов
        self.callback(clicks_per_second)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.delay = 0.01
        self.interval = 0.01
        self.duration = 1

        self.button = tk.Button(self, text="Calculate CPS", command=self.practical_cps)
        self.button.pack()

    def practical_cps(self):
        # Обработчик нажатия кнопки
        def handle_result(cps_result):
            print("Clicks per second:", cps_result)
            # Здесь можно выполнить обновление интерфейса или выполнить другие действия с результатом

        cps_thread = CPSCalculationThread(delay=self.delay, interval=self.interval,
                                          duration=self.duration, callback=handle_result)
        cps_thread.start()

app = App()
app.mainloop()
