"""GUI"""

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

from tkinter import font


import tkcalendar as tkc 

from excel import constants



class CustomWindow(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frames = dict()
        
    def AddFrame(self, name, frame):
        self._frames[name] = frame
    
    def ShowFrame(self, name):
        frame = self._frames.get(name)
        if frame is not None:
            frame.tkraise()
            

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

        CreateBareboneExcel(self, lower_frame, 0, 1)
        CreateNewSchedule(self, lower_frame, 0, 2)
        UpdateExistingSchedule(self, lower_frame, 0, 3)


class LowerFrame(tk.LabelFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inner_frame = None

        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        """
        tab_parent = ttk.Notebook(self)
        tab1 = ttk.Frame(tab_parent)
        tab2 = ttk.Frame(tab_parent)
        tab3 = ttk.Frame(tab_parent)

        tab_parent.add(tab1, text='설정1')
        tab_parent.add(tab2, text='설정2')
        tab_parent.add(tab3, text='설정3')


        tab_parent.pack(expand=True, fill=tk.BOTH)

        """


    def destroyInnerFrame(self):
        if self._inner_frame is not None:
            self._inner_frame.destroy()
    
    def ShowBareboneExcelFrame(self):
        self.destroyInnerFrame()
        f = BareboneExcelFrame(self)
        f.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)
        return
        

        #label = tk.Label(self, text='새 엑셀 파일 라벨')
        #label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        frame = tk.Frame(self)
        frame.grid_columnconfigure(0, weight=1, uniform='group1')
        frame.grid_columnconfigure(1, weight=1, uniform='group1')
        frame.grid_rowconfigure(0, weight=1, uniform='group2')
        # frame.pack()

        label1 = tk.Label(frame, text='여기는 간호사 이름들 넣기')
        label1.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        label2 = tk.Label(frame, text='여기는 시작날짜 - 끝날짜 넣기')
        label2.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)




    def ShowNewScheduleFrame(self):
        self.destroyInnerFrame()
        label = tk.Label(self, text='새 일정 라벨')
        label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    def ShowUpdateExistingScheduleFrame(self):
        self.destroyInnerFrame()
        label = tk.Label(self, text='일정 수정 라벨')
        label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)


class BareboneExcelFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_columnconfigure(1, weight=2, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        left_frame = tk.Frame(self)
        left_frame.grid_rowconfigure(0, weight=1, uniform='group1')
        left_frame.grid_rowconfigure(1, weight=9, uniform='group1')
        left_frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)


        right_frame = tk.Frame(self)
        right_frame.grid_rowconfigure(0, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(1, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(2, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(3, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(4, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(5, weight=4, uniform='group1')
        right_frame.grid_rowconfigure(6, weight=1, uniform='group1')
        right_frame.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        # Configure left-side
        label = tk.Label(left_frame, text='간호사 이름을 입력하세요')
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  # Why does 'NEWS' not work?
        text_area = tk.Text(left_frame)
        text_area.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        # Configure right-side
        
        # date widgets
        label2 = tk.Label(right_frame, text='시작날짜')
        label2.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)
        cal = tkc.DateEntry(right_frame, year=2020, month=5, day=1)
        cal.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)
        label3 = tk.Label(right_frame, text='끝날짜')
        label3.grid(row=2, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)
        cal2 = tkc.DateEntry(right_frame, year=2020, month=5, day=31)
        cal2.grid(row=3, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

        # Instruction label
        instruction = """
        사용 방법
        1.간호사 이름을 한줄씩 적어주세요
        2.일정의 시작-끝 날짜를 지정합니다
        3."엑셀 파일 받기"를 눌러 파일을 저장합니다
        4."날짜별 설정" 시트에서 필요 인원을 입력합니다
        5."간호사별 설정"에서 근무일수를 입력합니다
        6."일정표"에서 기존에 정해진 일정을 입력합니다
        7."새 일정" 탭에서 다음 단계를 진행해 주세요
        """
        instruction_label = tk.Label(right_frame, text=instruction, justify=tk.LEFT)
        instruction_label.grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)

        # Download button
        def callback_func():
            filename = filedialog.asksaveasfilename(title='기본 엑셀 파일 저장하기')
            
        download_button = tk.Button(right_frame, text='기본 엑셀 파일 다운 받기', command=callback_func)
        download_button.grid(row=6, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)



def CreateBareboneExcel(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)

    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    def callback_func(): 
        lower_frame.ShowBareboneExcelFrame()
 
    button_label = tk.Button(frame, text='기본 엑셀 파일 받기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def CreateBareboneExcelConfigFrame(root):
    frame = tk.Frame(root)
    #frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text='테스트 텍스트1s1 '*5)
    label.pack(fill=tk.BOTH, expand=True)

    return frame


def CreateNewSchedule(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)


    def callback_func(): 
        lower_frame.ShowNewScheduleFrame()

    button_label = tk.Button(frame, text='새 일정 넣기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)




def UpdateExistingSchedule(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    def callback_func(): 
        lower_frame.ShowUpdateExistingScheduleFrame()

    button_label = tk.Button(frame, text='기존 일정 수정하기', command=callback_func)
    button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def CreateMainFrame(root, lower_frame):
    main_frame = tk.Frame(root)
    #main_frame.pack(fill=tk.BOTH, expand=True)

    main_frame.grid_columnconfigure(0, weight=1, uniform='group1')
    main_frame.grid_columnconfigure(1, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(2, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(3, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(4, weight=1, uniform='group1')
    main_frame.grid_rowconfigure(0, weight=1, uniform='group2')

    CreateBareboneExcel(main_frame, lower_frame, 0, 1)
    CreateNewSchedule(main_frame, lower_frame, 0, 2)
    UpdateExistingSchedule(main_frame, lower_frame, 0, 3)



    
    
    return main_frame


def CreateNewExcelFrame(root):
    frame = tk.Frame(root)
    #frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text='테스트 텍스트111 '*5)
    label.pack(fill=tk.BOTH, expand=True)

    return frame
    


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
    root = CustomWindow()
    root.minsize(800, 600)
    root.maxsize(800, 600)
    #root.maxsize(1280, 960)
    root.title('테스트 타이틀')

    root.grid_rowconfigure(0, weight=1, uniform='group2')
    root.grid_rowconfigure(1, weight=4, uniform='group2')
    root.grid_columnconfigure(0, weight=1, uniform='group1')

    lower_frame = LowerFrame(root, text='내용')
    lower_frame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)



    #upper_frame = CreateMainFrame(root, lower_frame)
    upper_frame = UpperFrame(root, lower_frame)
    upper_frame.grid(row=0, column=0)
    
    

    CreateMenuBar(root)

    return root


if __name__ == '__main__':
    #s = ttk.Style()
    #print(s.theme_names())
    #s.theme_use('xpnative')
    #s.configure(, foreground='blue')
    root = CreateGUI()

    #s = tk.Style()
    #s.theme_use('vista')
    #s.configure(root.winfo_class(), foreground='red')
    
    root.mainloop()
    
    