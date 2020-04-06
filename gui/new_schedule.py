import tkinter as tk
import util


class NewScheduleFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = tk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 2, 1, 2, 1))
       
        # Button to open partially filled barebone filed
        open_file_button = tk.Button(left_frame, text='기본 엑셀 파일 불러오기')
        util.SetGrid(open_file_button, 0, 0)
        # Opened file name. Empty label if no file is loaded
        open_file_label = tk.Label(left_frame, text='현재 파일: sample.xlsx')
        util.SetGrid(open_file_label, 1, 0)

        # Start date, end date of new schedule
        start_date_label = tk.Label(left_frame, text='일정 시작 날짜: 2020년 5월 1일')
        util.SetGrid(start_date_label, 2, 0)
        end_date_label = tk.Label(left_frame, text='일정 종료 날짜: 2020년 5월 31일')
        util.SetGrid(end_date_label, 3, 0)

        # How long should the solver run?
        max_time_frame = tk.Frame(left_frame)
        util.SetGridWeights(max_time_frame, column_weights=(4, 1, 1))
        util.SetGrid(max_time_frame, 6, 0)

        max_time_label1 = tk.Label(max_time_frame, text='최대 검색 시간')
        util.SetGrid(max_time_label1, 0, 0)

        spinbox = tk.Spinbox(max_time_frame, from_=1, to=30)
        util.SetGrid(spinbox, 0, 1)

        max_time_label2 = tk.Label(max_time_frame, text='분')
        util.SetGrid(max_time_label2, 0, 2)

        # Notice that the solver will stop after the specific time
        max_time_info_label = tk.Label(left_frame, text='시간 내로 조건에 맞는 일정을 찾을 수 없을 시\n작업을 중지합니다')
        util.SetGrid(max_time_info_label, 7, 0)

        # Start button. Click will validate the input Excel and run the solver
        submit_button = tk.Button(left_frame, text='시작')
        util.SetGrid(submit_button, 8, 0)

    def createRightFrame(self):
        right_frame = tk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        # Right side of the frame only displays status (of validation and solver run)
        label = tk.Label(right_frame, text='진행상황')
        util.SetGrid(label, 0, 0)
        text_area = tk.Text(right_frame, state=tk.DISABLED)
        util.SetGrid(text_area, 1, 0)
