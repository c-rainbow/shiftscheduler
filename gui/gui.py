"""GUI"""
import barebone
import new_schedule
import update_schedule

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import tkcalendar as tkc 

           
class UpperFrame(tk.Frame):

    def __init__(self, master, lower_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._lower_frame = lower_frame

        # Configure layouts
        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_columnconfigure(1, weight=2, uniform='group1')
        self.grid_columnconfigure(2, weight=2, uniform='group1')
        self.grid_columnconfigure(3, weight=2, uniform='group1')
        self.grid_columnconfigure(4, weight=1, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        CreateBareboneExcelButton(self, lower_frame, 0, 1)
        CreateNewScheduleButton(self, lower_frame, 0, 2)
        UpdateScheduleButton(self, lower_frame, 0, 3)


class LowerFrame(tk.LabelFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        self.barebone_frame = barebone.BareboneExcelFrame(self)
        self.new_schedule_frame = new_schedule.NewScheduleFrame(self)
        self.update_schedule_frame = update_schedule.UpdateScheduleFrame(self)
        
        self.current_frame = None

    def ShowBareboneFrame(self):
        self.showFrame(self.barebone_frame)

    def ShowNewScheduleFrame(self):
        self.showFrame(self.new_schedule_frame)

    def ShowUpdateScheduleFrame(self):
        self.showFrame(self.update_schedule_frame)

    def showFrame(self, frame_to_show):
        if self.current_frame is not None:
            self.current_frame.grid_forget()
        self.current_frame = frame_to_show
        self.current_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)


def CreateBareboneExcelButton(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)

    frame.grid(row=row_index, column=col_index, sticky=tk.NSEW, padx=5, pady=5)

    def callback_func(): 
        lower_frame.ShowBareboneFrame()
 
    button_label = tk.Button(frame, text='기본 엑셀 파일 받기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.NSEW)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def CreateNewScheduleButton(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.NSEW, padx=5, pady=5)


    def callback_func(): 
        lower_frame.ShowNewScheduleFrame()

    button_label = tk.Button(frame, text='새 일정 넣기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.NSEW)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def UpdateScheduleButton(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.NSEW, padx=5, pady=5)

    def callback_func(): 
        lower_frame.ShowUpdateScheduleFrame()

    button_label = tk.Button(frame, text='기존 일정 수정하기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.NSEW)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


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

    root.grid_rowconfigure(0, weight=1, uniform='group2')
    root.grid_rowconfigure(1, weight=4, uniform='group2')
    root.grid_columnconfigure(0, weight=1, uniform='group1')

    lower_frame = LowerFrame(root)
    lower_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)

    upper_frame = UpperFrame(root, lower_frame)
    upper_frame.grid(row=0, column=0)

    CreateMenuBar(root)

    return root


if __name__ == '__main__':
    root = CreateGUI()
    root.mainloop()
