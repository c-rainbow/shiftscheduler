
import tkcalendar as tkc 
import tkinter as tk
from tkinter import filedialog


# TkInter frame for getting barebone Excel file
class BareboneExcelFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_columnconfigure(1, weight=2, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        self.createLeftFrame()
        self.createRightFrame()

    # Create left side of the frame
    def createLeftFrame(self):
        left_frame = tk.Frame(self)
        left_frame.grid_rowconfigure(0, weight=1, uniform='group1')
        left_frame.grid_rowconfigure(1, weight=9, uniform='group1')
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        label = tk.Label(left_frame, text='간호사 이름을 입력하세요')
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  # For some reason, tk.NSEW does not work
        text_area = tk.Text(left_frame)
        text_area.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)

    # Create right side of the frame
    def createRightFrame(self):
        right_frame = tk.Frame(self)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        weights = (1, 1, 1, 1, 1, 4, 1)
        for i, w in enumerate(weights):
            right_frame.grid_rowconfigure(i, weight=w, uniform='group1')
        
        # Start date widgets
        start_date_label = tk.Label(right_frame, text='시작날짜')
        start_date_label.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        start_cal = tkc.DateEntry(right_frame, year=2020, month=5, day=1)
        start_cal.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # End date widgets
        end_date_label = tk.Label(right_frame, text='끝날짜')
        end_date_label.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        end_cal = tkc.DateEntry(right_frame, year=2020, month=5, day=31)
        end_cal.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)

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
            # TODO: Create configs and save to Excel
            
        download_button = tk.Button(right_frame, text='기본 엑셀 파일 다운 받기', command=callback_func)
        download_button.grid(row=6, column=0, sticky=tk.NSEW, padx=5, pady=5)