import PySimpleGUI as sg
import os.path

title=("Arial Bold",30)

layout = [
    [sg.Text("Generate New Model",size=(20, 1), text_color="black", font=title)],
    [sg.HorizontalSeparator(color="Black")],
    [sg.Button("Record Data",size=(15,5)), sg.Button("Stop Recording",size=(15,5))],
    [sg.HorizontalSeparator(color="Black")],
    [sg.Text("Import Data ",text_color="Black"), sg.Input(), sg.FileBrowse("Browse", key="-IN-")],
    [sg.HorizontalSeparator(color="Black")],
    [sg.Button("Generate Model",size=(15,5))]
]


# Create the window
window = sg.Window("ML Model Generator", layout, size=(600,600),element_justification='c')

# Create an event loop
while True:
    event, values = window.read()

    # End program if user closes window or
    # presses the OK button
    if event == sg.WIN_CLOSED:
        break

window.close()