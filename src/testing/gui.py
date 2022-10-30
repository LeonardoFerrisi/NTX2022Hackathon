import PySimpleGUI as sg
import os.path

title=("Arial Bold",30)
save_model_path=("XXX")
save_analysis_path=("XXX")

layout = [
    [sg.Text("Generate New Model", text_color="black", font=title)],
    [sg.HorizontalSeparator(color="Black")],
    [sg.Button("Record Data",size=(15,5)), sg.Button("Stop Recording",size=(15,5))],
    [sg.Text("Import Data ",text_color="Black"), sg.Input(), sg.FileBrowse("Browse", key="-IN-")],
    [sg.Button("Generate Model",size=(15,5))],
    [sg.HorizontalSeparator(color="Black")],
    [sg.Text("Run Model", text_color="black", font=title)],
    [sg.Text("Import Model ",text_color="Black"), sg.Input(), sg.FileBrowse("Browse", key="-IN-")],
    [sg.Button("Run Model",size=(15,5))]
]


# Create the window
window = sg.Window("ML Model Generator", layout, size=(600,600),element_justification='c')

# Create an event loop
while True:
    event, values = window.read()
    if event == "Record Data":
        sg.Popup('Recording...')
    elif event == "Stop Recording":
        sg.Popup('Stopped recording')
    elif event == "Generate Model":
        sg.Popup("Model Created! Directory:", save_model_path)
    elif event == "Run Model":
        sg.Popup("Model Executed! Directory:", save_analysis_path)

    # End program if user closes window or
    # presses the OK button
    if event == sg.WIN_CLOSED:
        break

window.close()