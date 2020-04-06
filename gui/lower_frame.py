
import barebone
import new_schedule
import update_schedule
import util
import tkinter as tk


class LowerFrame(tk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        util.SetGridWeights(self)  # single row, single column

        self.displayed_frame = None
        self.barebone_frame = barebone.BareboneExcelFrame(self)
        self.new_schedule_frame = new_schedule.NewScheduleFrame(self)
        self.update_schedule_frame = update_schedule.UpdateScheduleFrame(self)

    def ShowBareboneFrame(self):
        self.showFrame(self.barebone_frame)

    def ShowNewScheduleFrame(self):
        self.showFrame(self.new_schedule_frame)

    def ShowUpdateScheduleFrame(self):
        self.showFrame(self.update_schedule_frame)

    def showFrame(self, frame_to_show):
        if self.displayed_frame is not None:
            self.displayed_frame.grid_forget()
        self.displayed_frame = frame_to_show
        self.displayed_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        