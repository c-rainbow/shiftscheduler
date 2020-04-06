import tkinter as tk


# Set grid location with some default values
def SetGrid(widget, row, column, sticky=tk.NSEW, padx=5, pady=5):
    widget.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)


# Set grid weights in a frame
def SetGridWeights(frame, column_weights=(1,), row_weights=(1,)):
    for i, w in enumerate(column_weights):
        frame.grid_columnconfigure(i, weight=w, uniform='column_group')
    for i, w in enumerate(row_weights):
        frame.grid_rowconfigure(i, weight=w, uniform='row_group')