"""GUI"""
import lower_frame as lower
import upper_frame as upper
import util

import tkinter as tk
from tkinter import messagebox


def CreateMenuBar(root):
    menu = tk.Menu(root)
    
    filemenu = tk.Menu(menu, tearoff=0)
    filemenu.add_command(
        label='아무것도 안하는 버튼',
        command=lambda: tk.messagebox.showinfo(message='사실 이거 보여주기 위해 어그로 끌었다'))
    filemenu.add_command(label='무언가 할 것 같은 버튼')
    filemenu.add_command(label='종료')

    menu.add_cascade(label='파일', menu=filemenu)

    root.config(menu=menu)


def CreateGUI():
    root = tk.Tk()
    root.minsize(800, 600)
    root.maxsize(800, 600)
    root.title('교대근무 일정 프로그램 v0.1')

    util.SetGridWeights(root, row_weights=(1, 4))

    lower_frame = lower.LowerFrame(root)
    lower_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    upper_frame = upper.UpperFrame(root, lower_frame)
    upper_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    CreateMenuBar(root)

    return root


if __name__ == '__main__':
    root = CreateGUI()
    root.mainloop()
