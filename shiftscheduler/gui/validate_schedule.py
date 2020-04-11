
import os
import tkinter as tk
from tkinter import filedialog

from shiftscheduler.excel import input as excel_input
from shiftscheduler.gui import util
from shiftscheduler.validation import validator


class ValidateScheduleFrame(tk.Frame): 
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
       
        # Button to open updated Excel file
        open_file_button = tk.Button(left_frame, text='완성된 엑셀 파일 불러오기', command=self.openUpdatedExcel)
        util.SetGrid(open_file_button, 0, 0)
        # Opened file name. Empty label if no file is loaded
        open_file_label = tk.Label(left_frame, textvariable=self.open_filename_strv)
        util.SetGrid(open_file_label, 1, 0)

        # Start date, end date of new schedule
        start_date_label = tk.Label(left_frame, textvariable=self.start_date_strv)
        util.SetGrid(start_date_label, 2, 0)
        end_date_label = tk.Label(left_frame, textvariable=self.end_date_strv)
        util.SetGrid(end_date_label, 3, 0)

    def createRightFrame(self):
        right_frame = tk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        # Right side of the frame only displays status (of validation and solver run)
        label = tk.Label(right_frame, text='오류 확인창')
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

    def openUpdatedExcel(self):
        filepath = filedialog.askopenfilename(title='수정된 엑셀 파일 열기')
        if not filepath:
            return

        base_schedule = excel_input.ReadFromExcelFile(filepath)

        # Update labels
        start_date = base_schedule.software_config.start_date
        end_date = base_schedule.software_config.end_date
        self.updateLabels(filepath, start_date, end_date)

        # Validate
        errors = validator.ValidateTotalScheduleFormat(base_schedule, barebone=False)
        
        if errors:
            self.addToTextArea('\n'.join(errors))
        else:
            self.addToTextArea('오류가 없습니다\n')  # TODO: Add output time