
from tkinter import ttk

from shiftscheduler.gui import barebone
from shiftscheduler.gui import new_schedule
from shiftscheduler.gui import update_schedule
from shiftscheduler.gui import validate_schedule
from shiftscheduler.gui import util


class LowerFrame(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        util.SetGridWeights(self)  # single row, single column

        self.displayed_frame = None
        self.barebone_frame = barebone.BareboneExcelFrame(self)
        self.new_schedule_frame = new_schedule.NewScheduleFrame(self)
        self.update_schedule_frame = update_schedule.UpdateScheduleFrame(self)
        self.validate_schedule_frame = validate_schedule.ValidateScheduleFrame(self)

    def ShowBareboneFrame(self):
        self.showFrame(self.barebone_frame)

    def ShowNewScheduleFrame(self):
        self.showFrame(self.new_schedule_frame)

    def ShowUpdateScheduleFrame(self):
        self.showFrame(self.update_schedule_frame)

    def ShowValidateScheduleFrame(self):
        self.showFrame(self.validate_schedule_frame)

    def showFrame(self, frame_to_show):
        if self.displayed_frame is not None:
            self.displayed_frame.grid_forget()
        self.displayed_frame = frame_to_show
        util.SetGrid(self.displayed_frame, 0, 0)
        