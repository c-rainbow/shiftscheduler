
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

from shiftscheduler.excel import input as excel_input
from shiftscheduler.excel import output as excel_output
from shiftscheduler.gui import util
from shiftscheduler.i18n import gettext
from shiftscheduler.solver import input as solver_input
from shiftscheduler.solver import output as solver_output
from shiftscheduler.validation import validator


_ = gettext.GetTextFn('gui/new_schedule')


class NewScheduleFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.open_filename_strv = tk.StringVar(value='')
        self.start_date_strv = tk.StringVar(value='')
        self.end_date_strv = tk.StringVar(value='')
        self.max_time_var = tk.IntVar()

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = ttk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 2, 1, 2, 1))
       
        # Button to open partially filled barebone filed
        open_file_button = ttk.Button(
            left_frame, text=_('Load barebone Excel file'), command=self.openBareboneExcel)
        util.SetGrid(open_file_button, 0, 0)
        # Opened file name. Empty label if no file is loaded
        open_file_label = ttk.Label(left_frame, textvariable=self.open_filename_strv)
        util.SetGrid(open_file_label, 1, 0)

        # Start date, end date of new schedule
        start_date_label = ttk.Label(left_frame, textvariable=self.start_date_strv)
        util.SetGrid(start_date_label, 2, 0)
        end_date_label = ttk.Label(left_frame, textvariable=self.end_date_strv)
        util.SetGrid(end_date_label, 3, 0)

        # How long should the solver run?
        max_time_frame = ttk.Frame(left_frame)
        util.SetGridWeights(max_time_frame, column_weights=(4, 1, 1))
        util.SetGrid(max_time_frame, 6, 0)

        max_time_label1 = ttk.Label(max_time_frame, text=_('Maximum search time'))
        util.SetGrid(max_time_label1, 0, 0)

        self.max_time_var.set(1)
        spinbox = ttk.Spinbox(max_time_frame, from_=1, to=30, textvariable=self.max_time_var)
        util.SetGrid(spinbox, 0, 1)

        max_time_label2 = ttk.Label(max_time_frame, text=_('minutes'))
        util.SetGrid(max_time_label2, 0, 2)

        # Notice that the solver will stop after the specific time
        max_time_info_label = ttk.Label(
            left_frame, text=_('Search will stop after this time'))
        util.SetGrid(max_time_info_label, 7, 0)

        # Start button. Click will validate the input Excel and run the solver
        submit_button = ttk.Button(left_frame, text=_('Start Search'))
        util.SetGrid(submit_button, 8, 0)

    def createRightFrame(self):
        right_frame = ttk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        # Right side of the frame only displays status (of validation and solver run)
        label = ttk.Label(right_frame, text=_('Progress'))
        util.SetGrid(label, 0, 0)
        self.status_text_area = scrolledtext.ScrolledText(right_frame, state=tk.DISABLED)
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
        self.open_filename_strv.set(_('Selected file: {filename}') % filename)
        self.start_date_strv.set(_('Start date: {start_date}') % start_date)
        self.end_date_strv.set(_('End date: {end_date}') % end_date)

    def addToTextArea(self, text_to_add):
        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.insert(tk.END, text_to_add)
        self.status_text_area.configure(state=tk.DISABLED)

    def openBareboneExcel(self):
        filepath = filedialog.askopenfilename(title=_('Load barebone Excel file'))
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
            self.addToTextArea(_('Starting..\n'))
            solver, var_dict = solver_input.FromTotalSchedule(base_schedule)
            self.addToTextArea(_('Starting the solver\n'))
            
            max_time_ms = self.max_time_var.get() * 60 * 1000
            solver.set_time_limit(max_time_ms)
            status = solver.Solve()
            self.addToTextArea(_('The solver stopped. Result: {status}\n') % status)

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
            filepath = filedialog.asksaveasfilename(title=_('Save to..'))
            if filepath:
                excel_output.FromTotalSchedule(new_schedule, filepath)
