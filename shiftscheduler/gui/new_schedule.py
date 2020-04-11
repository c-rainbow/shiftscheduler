
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from shiftscheduler.excel import input as excel_input
from shiftscheduler.excel import output as excel_output
from shiftscheduler.gui import util
from shiftscheduler.solver import input as solver_input
from shiftscheduler.solver import output as solver_output
from shiftscheduler.validation import validator


class NewScheduleFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.open_filename_strv = tk.StringVar(value='')
        self.start_date_strv = tk.StringVar(value='')
        self.end_date_strv = tk.StringVar(value='')

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = tk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 2, 1, 2, 1))
       
        # Button to open partially filled barebone filed
        open_file_button = tk.Button(left_frame, text='기본 엑셀 파일 불러오기', command=self.openBareboneExcel)
        util.SetGrid(open_file_button, 0, 0)
        # Opened file name. Empty label if no file is loaded
        open_file_label = tk.Label(left_frame, textvariable=self.open_filename_strv)
        util.SetGrid(open_file_label, 1, 0)

        # Start date, end date of new schedule
        start_date_label = tk.Label(left_frame, textvariable=self.start_date_strv)
        util.SetGrid(start_date_label, 2, 0)
        end_date_label = tk.Label(left_frame, textvariable=self.end_date_strv)
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
        self.status_text_area = tk.Text(right_frame, state=tk.DISABLED)
        util.SetGrid(self.status_text_area, 1, 0)

    def clearFields(self):
        self.open_filename_strv.set('')
        self.start_date_strv.set('')
        self.end_date_strv.set('')

        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.delete(1.0, tk.END)
        self.status_text_area.configure(state=tk.DISABLED)

    def updateLabels(self, filepath, start_date, end_date):
        self.clearFields()
        filename = os.path.basename(filepath)
        self.open_filename_strv.set('선택한 파일: %s' % filename)
        self.start_date_strv.set('일정 시작 날짜: %s' % start_date)
        self.end_date_strv.set('일정 끝 날짜: %s' % end_date)

    def addToTextArea(self, text_to_add):
        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.insert(tk.END, text_to_add)
        self.status_text_area.configure(state=tk.DISABLED)

    def openBareboneExcel(self):
        filepath = filedialog.askopenfilename(title='기본 엑셀 파일 열기')
        if not filepath:
            return

        base_schedule = excel_input.ReadFromExcelFile(filepath)

        # Update labels
        start_date = base_schedule.software_config.start_date
        end_date = base_schedule.software_config.end_date
        self.updateLabels(filepath, start_date, end_date)

        # Validate
        errors = validator.ValidateTotalScheduleFormat(base_schedule, barebone=True)
        
        if errors:
            self.addToTextArea('\n'.join(errors))
        else:
            self.addToTextArea('시작합니다\n')
            solver, var_dict = solver_input.FromTotalSchedule(base_schedule)
            self.addToTextArea('solve 시작\n')
            # TODO: Add total running time
            status = solver.Solve()
            self.addToTextArea('solve 끝. 결과: %s\n' % status)

            if status == solver.INFEASIBLE:
                messagebox.showerror(message='가능한 일정이 없습니다. 조건을 변경해 주세요')
                return
            else:
                messagebox.showinfo(message='일정을 완성하였습니다. 저장할 파일 경로를 설정해 주세요')

            new_schedule = solver_output.ToTotalSchedule(
                base_schedule.software_config, base_schedule.person_configs, base_schedule.date_configs,
                var_dict)

            errors = validator.ValidateTotalScheduleFormat(new_schedule, barebone=False)
            if errors:
                self.addToTextArea('\n'.join(errors))
                return
      
            # Save to Excel file
            filepath = filedialog.asksaveasfilename(title='완성된 엑셀 파일 저장하기')
            if filepath:
                excel_output.FromTotalSchedule(new_schedule, filepath)
