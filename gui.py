




import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from tkinter import font





class CustomWindow(tk.Tk):
    
    # self = C++ this
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frames = dict()
        
    def AddFrame(self, name, frame):
        self._frames[name] = frame
    
    def ShowFrame(self, name):
        frame = self._frames.get(name)
        if frame is not None:
            frame.tkraise()
            

def CreateBareboneExcel(root, row_index, col_index):
    frame = tk.Frame(root)

    # 뭔가 일어남....



    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)
 
    button_label = ttk.Button(frame, text='기본 엑셀 파일 받기')
    button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def CreateNewSchedule(root, lower_frame, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    def callback_func(): 
        #root.master.master.ShowFrame('new_excel')
        new_excel_frame = CreateNewExcelFrame(lower_frame)
        new_excel_frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)



    button_label = ttk.Button(frame, text='New Schedule', command=callback_func)
    
    button_font = font.Font(name='궁서체', size=15)
    #button_label['font'] = button_font
    
    
    
    button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)




def UpdateExistingSchedule(root, row_index, col_index):
    frame = tk.Frame(root)
    frame.grid(row=row_index, column=col_index, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    

    #canvas = tk.Canvas(frame, width=200, height=200)
    #canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    #canvas.pack()
    #img = tk.PhotoImage(file='photo.png')
    #canvas.create_image(50, 50, image=image)

    #label = tk.Label(frame, image=img)
    #label.image = img
    #label.place(x=0, y=0)
    #label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    

    #button_label = ttk.Button(frame, text='기존 일정 수정하기',)
    #button_label.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    #button_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def CreateMainFrame(root, lower_frame):
    main_frame = tk.Frame(root)
    #main_frame.pack(fill=tk.BOTH, expand=True)

    main_frame.grid_columnconfigure(0, weight=1, uniform='group1')
    main_frame.grid_columnconfigure(1, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(2, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(3, weight=2, uniform='group1')
    main_frame.grid_columnconfigure(4, weight=1, uniform='group1')
    main_frame.grid_rowconfigure(0, weight=1, uniform='group2')
    #main_frame.grid_rowconfigure(1, weight=3, uniform='group2')
    #main_frame.grid_rowconfigure(2, weight=2, uniform='group2')
    # main_frame.grid_rowconfigure(2, weight=1, uniform='group2')

    CreateBareboneExcel(main_frame, 0, 1)
    CreateNewSchedule(main_frame, lower_frame, 0, 2)
    UpdateExistingSchedule(main_frame, 0, 3)



    
    
    return main_frame


def CreateNewExcelFrame(root):
    frame = tk.Frame(root)
    #frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text='테스트 텍스트111 '*10)
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
    root.title('테스트 타이틀')

    #container_frame = tk.Frame(root)
    # container_frame.pack(fill=tk.BOTH, expand=True)

    #container_frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)

    #container_frame.grid_columnconfigure(4, weight=1, uniform='group1')
    root.grid_rowconfigure(0, weight=1, uniform='group2')
    root.grid_rowconfigure(1, weight=4, uniform='group2')
    root.grid_columnconfigure(0, weight=1, uniform='group1')

    
    lower_frame = tk.LabelFrame(root, text='내용')
    lower_frame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S, padx=5, pady=5)

    upper_frame = CreateMainFrame(root, lower_frame)
    upper_frame.grid(row=0, column=0)
    
    # lower_frame.pack(fill=tk.BOTH, expand=True)
    #new_excel_frame = CreateNewExcelFrame(root)
    #main_frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
    #new_excel_frame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)

    # new_excel_frame.tkraise()

    #root.AddFrame('main', main_frame)
    #root.AddFrame('new_excel', new_excel_frame)

    CreateMenuBar(root)

    return root


if __name__ == '__main__':
    s = ttk.Style()
    #print(s.theme_names())
    s.theme_use('xpnative')
    #s.configure(, foreground='blue')
    root = CreateGUI()

    s = ttk.Style()
    s.theme_use('vista')
    #s.configure(root.winfo_class(), foreground='red')
    
    root.mainloop()
    
    