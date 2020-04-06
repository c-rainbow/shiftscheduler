

# Set grid weights in a frame
def SetGridWeights(frame, column_weights=(1,), row_weights=(1,)):
    for i, w in enumerate(column_weights):
        frame.grid_columnconfigure(i, weight=w, uniform='column_group')
    for i, w in enumerate(row_weights):
        frame.grid_rowconfigure(i, weight=w, uniform='row_group')