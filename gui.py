




import tkinter as tk
from tkinter import messagebox



def buttonCallback():
    messagebox.showinfo(title='this is title', message='hello this is a message')



def CreateBareboneExcel(root, row_index, col_index):
    frame = tk.LabelFrame(root, text='빈 엑셀 파일')
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    button_label = tk.Button(frame, text='빈 엑셀 파일')
    button_label.grid(row=0, column=0, sticky=tk.E)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def CreateNewSchedule(root, row_index, col_index):
    frame = tk.LabelFrame(root, text='새 일정 만들기')
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    button_label = tk.Button(frame, text='새 일정 만들기')
    button_label.grid(row=0, column=0, sticky=tk.E)


def UpdateExistingSchedule(root, row_index, col_index):
    frame = tk.LabelFrame(root, text='기존 일정 수정하기')
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    button_label = tk.Button(frame, text='기존 일정 수정하기')
    button_label.grid(row=0, column=0, sticky=tk.E)


def DoNothing(root, row_index, col_index):
    frame = tk.LabelFrame(root, text='그냥 있는 버튼')
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    button_label = tk.Button(frame, text='그냥 있는 버튼')
    button_label.grid(row=0, column=0, sticky=tk.E)


def CreateGUI():
    root = tk.Tk()
    root.minsize(400, 400)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    main_frame.grid_columnconfigure(0, weight=1, uniform='group1')
    main_frame.grid_columnconfigure(1, weight=1, uniform='group1')
    main_frame.grid_rowconfigure(0, weight=1, uniform='group2')
    main_frame.grid_rowconfigure(1, weight=1, uniform='group2')
    # main_frame.grid_rowconfigure(2, weight=1, uniform='group2')

    CreateBareboneExcel(main_frame, 0, 0)
    CreateNewSchedule(main_frame, 0, 1)
    UpdateExistingSchedule(main_frame, 1, 0)
    DoNothing(main_frame, 1, 1)    

    return root

if __name__ == '__main__':
    root = CreateGUI()
    root.mainloop()