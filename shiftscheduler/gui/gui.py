"""GUI"""

import tkinter as tk
from tkinter import messagebox

from shiftscheduler.gui import lower_frame as lower
from shiftscheduler.gui import upper_frame as upper
from shiftscheduler.gui import util


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
    root.minsize(900, 600)
    root.maxsize(900, 600)
    root.title('교대근무 일정 프로그램 v0.1')
    util.SetGridWeights(root, row_weights=(1, 4))

    lower_frame = lower.LowerFrame(root)
    util.SetGrid(lower_frame, 1, 0)
    upper_frame = upper.UpperFrame(root, lower_frame)
    util.SetGrid(upper_frame, 0, 0)

    CreateMenuBar(root)

    return root
