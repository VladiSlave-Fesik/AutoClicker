import tkinter as tk

click_actions = {
    0: "Left click",
    1: "Right click",
    2: "Middle click"
}

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Button Update')

        self.button = 0

        self.current_button_label = tk.Label(self.window, text=f'Current click: {click_actions[self.button]}')
        self.current_button_label.grid()

        self.click_button_input = tk.Entry()
        self.click_button_input.insert(0, str(self.button))
        self.click_button_input.grid()

        self.click_button_input.bind("<KeyRelease>", self.update_button_label)

        self.window.mainloop()

    def update_button_label(self, event):
        try:
            button = int(self.click_button_input.get())
            self.button = button
            self.current_button_label.config(text=f'Current click: {click_actions.get(button, "")}')
        except ValueError:
            pass


app = App()
