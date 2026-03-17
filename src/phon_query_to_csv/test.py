import tkinter as tk
import tkinter.font as tkfont
import tkinter.filedialog as tkfiledialog

def test_page(parameters):
    l_test = tk.Label(root, text = "Test!", font = tkfont.Font(family = "Arial", size = 16, weight = tkfont.NORMAL))
    l_test.grid(row = 0, column = 0)

    print(parameters)

def next(widgets, parameters, page):
    for widget in widgets:
        widget.place_forget()

    page(parameters)

def specifications(parameters):
    widgets = []

    l_prompt = tk.Label(root, text = "Would you like to run the default values?", font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL))
    l_prompt.place(relx = 0.5, x = 0, y = 200, anchor = "n")

    widgets.append(l_prompt)

    b_yes = tk.Button(root, text = "Yes", width = 5, height = 2, font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL), command = lambda : next(widgets, parameters, test_page))
    b_yes.place(relx = 0.5, x = -40, y = 240, anchor = "n")

    widgets.append(b_yes)

    b_no = tk.Button(root, text = "No", width = 5, height = 2, font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL), command = lambda : next(widgets, parameters, test_page))
    b_no.place(relx = 0.5, x = 40, y = 240, anchor = "n")

    widgets.append(b_no)

def directory_select(widgets, parameters):
    dir = tkfiledialog.askdirectory(initialdir = "/", title = "Select a Directory")

    parameters["Directory"] = dir

    next(widgets, parameters, specifications)

def directory(parameters):
    widgets = []

    l_prompt = tk.Label(root, text = "Please choose the directory of analysis", font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL))
    l_prompt.place(relx = 0.5, x = 0, y = 200, anchor = "n")

    widgets.append(l_prompt)

    b_browse = tk.Button(root, text = "Browse Directories", width = 20, height = 2, font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL), command = lambda : directory_select(widgets, parameters))
    b_browse.place(relx = 0.5, x = 0, y = 240, anchor = "n")

    widgets.append(b_browse)

def start(parameters):
    widgets = []

    b_start = tk.Button(root, text = "Start", width = 5, height = 2, font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL), command = lambda : next(widgets, parameters, directory))
    b_start.place(relx = 0.5, x = 0, y = 440, anchor = "n")

    widgets.append(b_start)

if __name__ == "__main__":
    parameters = {
        "Directory" : None
    }

    root = tk.Tk()
    root_w = 800
    root_h = 600

    root.title("Phon Query to CSV")
    root.geometry(str(root_w) + "x" + str(root_h))

    debug_frame = tk.Frame(root, width = root_w, height = root_h, highlightbackground = "red", highlightthickness = 4)
    debug_frame.place(relx = 0.5, rely = 0, x = 0, y = 0, anchor = "n")

    l_title = tk.Label(root, text = "Phon Query to CSV", font = tkfont.Font(family = "Arial", size = 32, weight = tkfont.BOLD, underline = 1))
    l_title.place(relx = 0.5, x = 0, y = 60, anchor = "n")

    l_subtitle = tk.Label(root, text = "A Visual Interface Assistance", font = tkfont.Font(family = "Arial", size = 20, weight = tkfont.BOLD))
    l_subtitle.place(relx = 0.5, x = 0, y = 120, anchor = "n")

    b_quit = tk.Button(root, text = "Quit", width = 5, height = 2, font = tkfont.Font(family = "Arial", size = 12, weight = tkfont.NORMAL), command = lambda : root.destroy())
    b_quit.place(relx = 0.5, x = 0, y = 500, anchor = "n")

    start(parameters)

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