
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

import tkcalendar as tkc

from shiftscheduler.excel import input as excel_input
from shiftscheduler.excel import output as excel_output
from shiftscheduler.gui import constants
from shiftscheduler.gui import util
from shiftscheduler.i18n import gettext
from shiftscheduler.solver import input as solver_input
from shiftscheduler.solver import output as solver_output
from shiftscheduler.validation import validator


_ = gettext.GetTextFn('gui/update_schedule')
DATE_PATTERN = _('y/m/d')
LOCALE_CODE = gettext.GetLanguageCode()


class UpdateScheduleFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.open_filename_strv = tk.StringVar(value='')
        self.start_date_cal = None  # To be assigned when DateEntry is created
        self.end_date_cal = None  # To be assigned when DateEntry is created
        self.keep_offdate_var = tk.BooleanVar()
        self.max_time_var = tk.IntVar()

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = ttk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 2, 1))

        # Open modified schedule
        open_file_button = ttk.Button(
            left_frame, text=_('Load file'), command=self.openExcelToUpdate)
        util.SetGrid(open_file_button, 0, 0)
        open_file_label = ttk.Label(left_frame, textvariable=self.open_filename_strv)
        util.SetGrid(open_file_label, 1, 0)

        # Select date range to update
        start_date_label = ttk.Label(left_frame, text=_('Update start date'))
        util.SetGrid(start_date_label, 2, 0)
        self.start_date_cal = tkc.DateEntry(
            left_frame, year=2020, month=5, day=1, date_pattern=DATE_PATTERN, locale=LOCALE_CODE)
        util.SetGrid(self.start_date_cal, 3, 0)
        # End date to update
        end_date_label = ttk.Label(left_frame, text=_('Update end date'))
        util.SetGrid(end_date_label, 4, 0)
        self.end_date_cal = tkc.DateEntry(
            left_frame, year=2020, month=5, day=31, date_pattern=DATE_PATTERN, locale=LOCALE_CODE)
        util.SetGrid(self.end_date_cal, 5, 0)

        # Checkbox to keep the off dates
        keep_offdate_checkbox = ttk.Checkbutton(
            left_frame, text=_('Keep the OFF dates'), variable=self.keep_offdate_var,
            onvalue=True, offvalue=False)
        util.SetGrid(keep_offdate_checkbox, 6, 0)

        # Max search time frame
        max_time_frame = ttk.Frame(left_frame)
        util.SetGrid(max_time_frame, 7, 0)
        util.SetGridWeights(max_time_frame, column_weights=(4, 1, 1))
        
        max_time_label1 = ttk.Label(max_time_frame, text=_('Maximum search time'))
        util.SetGrid(max_time_label1, 0, 0)

        self.max_time_var.set(1)
        max_time_spinbox = ttk.Spinbox(max_time_frame, from_=1, to=30, textvariable=self.max_time_var)
        util.SetGrid(max_time_spinbox, 0, 1)

        max_time_label2 = ttk.Label(max_time_frame, text=_('minutes'))
        util.SetGrid(max_time_label2, 0, 2)

        max_time_info_label = ttk.Label(
            left_frame, text=_('Search will stop after this time'))
        util.SetGrid(max_time_info_label, 8, 0)

        # Start button
        submit_button = ttk.Button(left_frame, text=_('Start'), command=self.updateSchedule)
        util.SetGrid(submit_button, 9, 0)

    def createRightFrame(self):
        # Right side only displays status of validation and solver run
        right_frame = ttk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        label = ttk.Label(right_frame, text=_('Progress'))
        util.SetGrid(label, 0, 0)
        self.status_text_area = scrolledtext.ScrolledText(right_frame, state=tk.DISABLED)
        util.SetGrid(self.status_text_area, 1, 0)
        

    def clearFields(self):
        self.open_filename_strv.set('')

        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.delete(1.0, tk.END)
        self.status_text_area.configure(state=tk.DISABLED)

    def updateLabels(self, filepath, start_date, end_date):
        self.clearFields()
        filename = os.path.basename(filepath)
        self.open_filename_strv.set(_('Selected file: {filename}').format(filename=filename))

    def addToTextArea(self, text_to_add):
        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.insert(tk.END, text_to_add)
        self.status_text_area.configure(state=tk.DISABLED)

    def updateSchedule(self):
        update_start_date = self.start_date_cal.get_date()
        update_end_date = self.end_date_cal.get_date()
        keep_offdates = self.keep_offdate_var.get()

        if update_start_date > update_end_date:
            self.addToTextArea(_('The start date is after the end date\n'))
            return

        excel_start_date = self.base_schedule.software_config.start_date        
        excel_end_date = self.base_schedule.software_config.end_date        
        if update_start_date < excel_start_date:
            self.addToTextArea(_('Update start date is before the schedule start date\n'))
            return
        if excel_end_date < update_end_date:
            self.addToTextArea(_('Update end date is after the schedule end date\n'))
            return

        solver, var_dict = solver_input.FromTotalSchedule(
            self.base_schedule, exclude_start=update_start_date, exclude_end=update_end_date,
            keep_offdates=keep_offdates)
        self.addToTextArea(_('Starting the solver...\n'))
        
        max_time_ms = self.max_time_var.get() * 60 * 1000
        solver.set_time_limit(max_time_ms)
        status = solver.Solve()
        self.addToTextArea(_('The solver stopped. Result: {status}\n').format(status=status))

        if status == solver.INFEASIBLE:
            messagebox.showerror(message=_('No solution is found. Please check the conditions'))
            return
        else:
            messagebox.showinfo(message=_('Completed the schedule. Please choose the location to save it'))

        new_schedule = solver_output.ToTotalSchedule(
            base_schedule.software_config, base_schedule.person_configs, base_schedule.date_configs,
            var_dict)

        errors = validator.ValidateTotalScheduleFormat(new_schedule, barebone=False)
        if errors:
            self.addToTextArea('\n'.join(errors))
            return
    
        # Save to Excel file
        filepath = filedialog.asksaveasfilename(title=_('Save to..'), filetypes=constants.EXCEL_FILE_TYPE)
        if filepath:
            excel_output.FromTotalSchedule(new_schedule, filepath)

    def openExcelToUpdate(self):
        filepath = filedialog.askopenfilename(
            title=_('Open schedule file to update'), filetypes=constants.EXCEL_FILE_TYPE)
        if not filepath:
            return

        self.base_schedule = excel_input.ReadFromExcelFile(filepath)

        # Update labels
        start_date = self.base_schedule.software_config.start_date
        end_date = self.base_schedule.software_config.end_date
        self.updateLabels(filepath, start_date, end_date)

        # Validate
        errors = validator.ValidateTotalScheduleFormat(self.base_schedule, barebone=True)
        
        if errors:
            self.addToTextArea('\n'.join(errors))
        else:
            self.addToTextArea(_('No error is found. Please click Start button\n'))
