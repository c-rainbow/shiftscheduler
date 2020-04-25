"""GUI"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from shiftscheduler.gui import lower_frame as lower
from shiftscheduler.gui import upper_frame as upper
from shiftscheduler.gui import util
from shiftscheduler.i18n import gettext


_ = gettext.GetTextFn('gui/gui')


def CreateGUI():
    root = tk.Tk()
    root.minsize(900, 600)
    root.maxsize(900, 600)
    root.title(_('Shift Scheduler v0.1'))
    util.SetGridWeights(root, row_weights=(1, 4))

    lower_frame = lower.LowerFrame(root)
    util.SetGrid(lower_frame, 1, 0)
    upper_frame = upper.UpperFrame(root, lower_frame)
    util.SetGrid(upper_frame, 0, 0)

    return root
