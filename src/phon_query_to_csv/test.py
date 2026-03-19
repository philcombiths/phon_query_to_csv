from tkinter import Tk

from tkinter import Frame
from tkinter import Label
from tkinter import Button
from tkinter import font

from tkinter import filedialog as dialog

def test(stage, parameters):
    text = Label(stage, text = "Test!")
    text.place(relx = 0.5, x = 0, y = 20, anchor = "center")

def specifications(stage, parameters):
    prompt = Label(stage, text = "Would you like to run the default values?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    yes = Button(stage, text = "Yes", width = 5)
    yes.place(relx = 0.5, x = -40, y = 60, anchor = "n")

    yes.config(command = lambda : sketch(stage, test, parameters, None, None))

    no = Button(stage, text = "No", width = 5)
    no.place(relx = 0.5, x = 40, y = 60, anchor = "n")

    no.config(command = lambda : sketch(stage, test, parameters, None, None))

def directory(stage, parameters):
    prompt = Label(stage, text = "Please choose the directory of analysis")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    browse = Button(stage, text = "Browse Directories", width = 20)
    browse.place(relx = 0.5, x = 0, y = 60, anchor = "n")

    browse.config(command = lambda : sketch(stage, specifications, parameters, "Directory", dialog.askdirectory(initialdir = "/", title = "Select a Directory")))

def start(stage, parameters):
    start = Button(stage, text = "Start", width = 5)
    start.place(relx = 0.5, x = 0, y = 320, anchor = "s")
    
    start.config(command = lambda : sketch(stage, directory, parameters, None, None))

def sketch(stage, scene, parameters, key, val):
    if key and val:
        parameters[key] = val

        print(parameters)

    for widget in stage.winfo_children():
        widget.destroy()

    scene(stage, parameters)

if __name__ == "__main__":
    parameters = {
        "Directory" : None
    }

    root = Tk()

    root.title("Phon Query to CSV")
    root.geometry("800x600")

    debug = Frame(root, width = 800, height = 600, highlightbackground = "red", highlightthickness = 1)
    debug.place(relx = 0.5, rely = 0, x = 0, y = 0, anchor = "n")

    font.nametofont("TkDefaultFont").configure(size = 12)

    title = Label(root, text = "Phon Query to CSV")
    title.place(relx = 0.5, x = 0, y = 60, anchor = "n")

    title.configure(font = font.Font(size = 32, weight = font.BOLD, underline = 1))

    subtitle = Label(root, text = "A Visual Interface Assistance")
    subtitle.place(relx = 0.5, x = 0, y = 120, anchor = "n")

    subtitle.configure(font = font.Font(size = 20, weight = font.BOLD))

    quit = Button(root, text = "Quit", width = 5)
    quit.place(relx = 0.5, x = 0, y = 500, anchor = "n")

    quit.configure(command = lambda : root.destroy())

    stage = Frame(root, width = 650, height = 320, highlightbackground = "red", highlightthickness = 1)
    stage.place(relx = 0.5, rely = 0, x = 0, y = 330, anchor = "center")

    sketch(stage, start, parameters, None, None)

    root.mainloop()  # Keeps the window open

"""

Would you like to run the default values? {

    (Yes)

    (No) {

        Which flavor would you like to employ?

            (TX)

            (Typology)

            (New Typology)

            (ITOLD)

            (NCJC)

            (Custom) {
                
                Enter participant regex:

                    [Input]

                Enter phase regex:

                    [Input]

                Select if Target and Actual are enabled:

                    [Target]

                    [Actual]

                (Finish)

            }

        Would you like to overwrite existing files?

            (Yes)

            (No)

        Select which steps you would like to run:

            [Gen_CSV]

            [Merge]

            [Accuracy]

            [Expand]

            [Pivot]

            (Finish)

        IF PIVOT ~ Would you like to blank repeated labels in the pivot table?

            (Yes)
            
            (No)

    }

}

The current parameters are as follows:

[Parameters]

Proceed? {

    (Yes)

    (No)

}

[Program Status Log]

"""