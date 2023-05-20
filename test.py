import tkinter as tk
from tkinter import filedialog

def save_as():
    file_path = filedialog.asksaveasfilename(
        initialdir="/",  # Начальная директория
        title="Save As",  # Заголовок диалогового окна
        filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
    )

    if file_path:
        if file_path.endswith('.ini'):
            print('ini')
        else:
            file_path += '.ini'
        print("Selected file path:", file_path)


root = tk.Tk()

button = tk.Button(root, text="Save As", command=save_as)
button.pack()

root.mainloop()
