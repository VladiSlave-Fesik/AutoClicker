import tkinter as tk

def save_button_click():
    # Обработчик нажатия кнопки сохранения
    print("Button clicked")

# Создание окна
window = tk.Tk()

# Создание значка сохранения
save_icon = tk.PhotoImage(file="data/images/key_1.png")

# Создание кнопки с сохранением
save_button = tk.Button(window, image=save_icon, command=save_button_click, bd=0, highlightthickness=0)
save_button.pack()

# Запуск главного цикла окна
window.mainloop()

