import tkinter as tk
import tkcalendar as tkc


class UpdateScheduleFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1, uniform='group1')
        self.grid_columnconfigure(1, weight=2, uniform='group1')
        self.grid_rowconfigure(0, weight=1, uniform='group2')

        self.createLeftFrame()
        self.createRightFrame()


    def createLeftFrame(self):
        left_frame = tk.Frame(self)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        left_frame.grid_columnconfigure(0, weight=1, uniform='group1')
        
        weights = (1, 1, 1, 1, 1, 1, 1, 1, 2, 1)
        for i, w in enumerate(weights):
            left_frame.grid_rowconfigure(i, weight=w, uniform='group1')

        # Open modified schedule
        open_file_button = tk.Button(left_frame, text='파일 불러오기')
        open_file_button.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        open_file_label = tk.Label(left_frame, text='현재 파일: sample.xlsx')
        open_file_label.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # Select date range to update
        label2 = tk.Label(left_frame, text='수정 시작 날짜')
        label2.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        cal = tkc.DateEntry(left_frame, year=2020, month=5, day=1)
        cal.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)
        # End date to update
        label3 = tk.Label(left_frame, text='수정 끝 날짜')
        label3.grid(row=4, column=0, sticky=tk.NSEW, padx=5, pady=5)
        cal2 = tkc.DateEntry(left_frame, year=2020, month=5, day=31)
        cal2.grid(row=5, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # Checkbox to keep the off dates
        keep_offdate_var = tk.IntVar()
        keep_offdate_checkbox = tk.Checkbutton(left_frame, text='기존의 오프날짜 유지', variable=keep_offdate_var)
        keep_offdate_checkbox.grid(row=6, column=0, sticky=tk.NSEW, padx=5, pady=5)


        max_time_frame = tk.Frame(left_frame)
        max_time_frame.grid_columnconfigure(0, weight=4, uniform='group1')
        max_time_frame.grid_columnconfigure(1, weight=1, uniform='group1')
        max_time_frame.grid_columnconfigure(2, weight=1, uniform='group1')
        max_time_frame.grid(row=7, column=0, sticky=tk.NSEW, padx=5, pady=5)

        max_time_label1 = tk.Label(max_time_frame, text='최대 검색 시간')
        max_time_label1.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        spinbox = tk.Spinbox(max_time_frame, from_=1, to=30)
        spinbox.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        max_time_label2 = tk.Label(max_time_frame, text='분')
        max_time_label2.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)


        max_time_info_label = tk.Label(left_frame, text='시간 내로 조건에 맞는 일정을 찾을 수 없을 시\n작업을 중지합니다')
        max_time_info_label.grid(row=8, column=0, sticky=tk.NSEW, padx=5, pady=5)

        submit_button = tk.Button(left_frame, text='시작')
        submit_button.grid(row=9, column=0, sticky=tk.NSEW, padx=5, pady=5)


    def createRightFrame(self):
        # Right side only displays status of validation and solver run
        right_frame = tk.Frame(self)
        right_frame.grid_rowconfigure(0, weight=1, uniform='group1')
        right_frame.grid_rowconfigure(1, weight=9, uniform='group1')
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        label = tk.Label(right_frame, text='진행상황')
        label.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        text_area = tk.Text(right_frame, state=tk.DISABLED)
        text_area.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)