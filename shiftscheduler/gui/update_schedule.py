
import tkinter as tk

import tkcalendar as tkc

from shiftscheduler.gui import util


class UpdateScheduleFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = tk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 2, 1))

        # Open modified schedule
        open_file_button = tk.Button(left_frame, text='파일 불러오기')
        util.SetGrid(open_file_button, 0, 0)
        open_file_label = tk.Label(left_frame, text='현재 파일: sample.xlsx')
        util.SetGrid(open_file_label, 1, 0)

        # Select date range to update
        label2 = tk.Label(left_frame, text='수정 시작 날짜')
        util.SetGrid(label2, 2, 0)
        cal = tkc.DateEntry(left_frame, year=2020, month=5, day=1)
        util.SetGrid(cal, 3, 0)
        # End date to update
        label3 = tk.Label(left_frame, text='수정 끝 날짜')
        util.SetGrid(label3, 4, 0)
        cal2 = tkc.DateEntry(left_frame, year=2020, month=5, day=31)
        util.SetGrid(cal2, 5, 0)

        # Checkbox to keep the off dates
        keep_offdate_var = tk.IntVar()
        keep_offdate_checkbox = tk.Checkbutton(left_frame, text='기존의 오프날짜 유지', variable=keep_offdate_var)
        util.SetGrid(keep_offdate_checkbox, 6, 0)

        max_time_frame = tk.Frame(left_frame)
        util.SetGrid(max_time_frame, 7, 0)
        util.SetGridWeights(max_time_frame, column_weights=(4, 1, 1))
        
        max_time_label1 = tk.Label(max_time_frame, text='최대 검색 시간')
        util.SetGrid(max_time_label1, 0, 0)

        spinbox = tk.Spinbox(max_time_frame, from_=1, to=30)
        util.SetGrid(spinbox, 0, 1)

        max_time_label2 = tk.Label(max_time_frame, text='분')
        util.SetGrid(max_time_label2, 0, 2)

        max_time_info_label = tk.Label(left_frame, text='시간 내로 조건에 맞는 일정을 찾을 수 없을 시\n작업을 중지합니다')
        util.SetGrid(max_time_info_label, 8, 0)

        submit_button = tk.Button(left_frame, text='시작')
        util.SetGrid(submit_button, 9, 0)

    def createRightFrame(self):
        # Right side only displays status of validation and solver run
        right_frame = tk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        label = tk.Label(right_frame, text='진행상황')
        util.SetGrid(label, 0, 0)
        text_area = tk.Text(right_frame, state=tk.DISABLED)
        util.SetGrid(text_area, 1, 0)
        