from tkinter import Tk

from tkinter import Frame
from tkinter import Label
from tkinter import Button
from tkinter import Entry
from tkinter import Checkbutton
from tkinter import font

from tkinter import StringVar
from tkinter import IntVar
from tkinter import filedialog as dialog

def test(stage, parameters):
    text = Label(stage, text = "Test!")
    text.place(relx = 0.5, x = 0, y = 20, anchor = "center")

    print(parameters)

def proceed(stage, parameters):
    prompt = Label(stage, text = "Would you like to proceed with the following parameters?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    line = 1

    for parameter in parameters.keys():
        line += 1
        
        partext = Label(stage, text = parameter + " : " + str(parameters[parameter]))
        partext.place(relx = 0, x = 20, y = line * 30, anchor = "nw")

    yes = Button(stage, text = "Yes", width = 5)
    yes.place(relx = 1, rely = 0.5, x = -40, y = -22, anchor = "ne")

    yes.config(command = lambda : sketch(stage, test, parameters, None))

    no = Button(stage, text = "No", width = 5)
    no.place(relx = 1, rely = 0.5, x = -40, y = 22, anchor = "ne")

    no.config(command = lambda : sketch(stage, fp, parameters, None))

def labelblank_set(stage, parameters, selection):
    updates = []

    if selection == "Yes":
        updates.append(["Blank Repeated Labels", True])

    if selection == "No":
        updates.append(["Blank Repeated Labels", False])

    sketch(stage, test, parameters, updates)

def labelblank(stage, parameters):
    prompt = Label(stage, text = "Would you like to blank repeated labels in the final pivot table?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    yes = Button(stage, text = "Yes", width = 5)
    yes.place(relx = 0.5, x = -40, y = 60, anchor = "n")

    yes.config(command = lambda : labelblank_set(stage, parameters, "Yes"))

    no = Button(stage, text = "No", width = 5)
    no.place(relx = 0.5, x = 40, y = 60, anchor = "n")

    no.config(command = lambda : labelblank_set(stage, parameters, "No"))

def fileow_set(stage, parameters, selection):
    updates = []

    if selection == "Yes":
        updates.append(["Overwrite", True])

    if selection == "No":
        updates.append(["Overwrite", False])

    sketch(stage, labelblank, parameters, updates)

def fileow(stage, parameters):
    prompt = Label(stage, text = "Would you like to overwrite existing files?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    yes = Button(stage, text = "Yes", width = 5)
    yes.place(relx = 0.5, x = -40, y = 60, anchor = "n")

    yes.config(command = lambda : fileow_set(stage, parameters, "Yes"))

    no = Button(stage, text = "No", width = 5)
    no.place(relx = 0.5, x = 40, y = 60, anchor = "n")

    no.config(command = lambda : fileow_set(stage, parameters, "No"))

def customflavor_set(stage, parameters, pha_re, par_re, target, actual):
    updates = []

    if pha_re and par_re:
        updates.append(["Phase Regex", pha_re])
        updates.append(["Participant Regex", par_re])
        updates.append(["Target", target == 1])
        updates.append(["Actual", actual == 1])
        sketch(stage, fileow, parameters, updates)
    else:
        sketch(stage, customflavor, parameters, updates)

def customflavor(stage, parameters):
    pha_re = StringVar()
    par_re = StringVar()
    target = IntVar()
    actual = IntVar()

    prompt_pha = Label(stage, text = "Please input the Phase Regex")
    prompt_pha.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    entry_pha = Entry(stage, textvariable = pha_re)
    entry_pha.place(relx = 0.5, x = 0, y = 50, anchor = "n")

    prompt_par = Label(stage, text = "Please input the Participant Regex")
    prompt_par.place(relx = 0.5, x = 0, y = 100, anchor = "n")

    entry_par = Entry(stage, textvariable = par_re)
    entry_par.place(relx = 0.5, x = 0, y = 130, anchor = "n")

    prompt_tar_act = Label(stage, text = "Please select if Target and Actual are enabled")
    prompt_tar_act.place(relx = 0.5, x = 0, y = 180, anchor = "n")

    check_tar = Checkbutton(stage, text = "Target", variable = target)
    check_tar.place(relx = 0.5, x = -80, y = 210, anchor = "n")

    check_act = Checkbutton(stage, text = "Actual", variable = actual)
    check_act.place(relx = 0.5, x = 80, y = 210, anchor = "n")

    submit = Button(stage, text = "Submit", width = 5)
    submit.place(relx = 0.5, x = 0, y = 320, anchor = "s")
    
    submit.config(command = lambda : customflavor_set(stage, parameters, pha_re.get(), par_re.get(), target.get(), actual.get()))

def flavor_set(stage, parameters, flavor):
    updates = []

    if flavor == "TX":
        updates.append(["Phase Regex", r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"])
        updates.append(["Participant Regex", r"\w\d\d\d"])
        updates.append(["Target", True])
        updates.append(["Actual", True])

    if flavor == "TX Blind":
        updates.append(["Phase Regex", r"\w{1}\d{4}"])
        updates.append(["Participant Regex", r"\w(?=\d{4})"])
        updates.append(["Target", True])
        updates.append(["Actual", True])

    if flavor == "Typology":
        updates.append(["Phase Regex", r"p[IVX]+"])
        updates.append(["Participant Regex", r"\d\d\d"])
        updates.append(["Target", False])
        updates.append(["Actual", True])

    if flavor == "New Typology":
        updates.append(["Phase Regex", r"no phases"])
        updates.append(["Participant Regex", r"\w{3,4}\d\d"])
        updates.append(["Target", False])
        updates.append(["Actual", True])

    if flavor == "ITOLD":
        updates.append(["Phase Regex", r"no phases"])
        updates.append(["Participant Regex", r"\w{4}\d{2}"])
        updates.append(["Target", True])
        updates.append(["Actual", True])

    if flavor == "NCJC":
        updates.append(["Phase Regex", r"Timepoint\d|Pre|Post|Fall|Spring|Winter|Summer"])
        updates.append(["Participant Regex", r"\w{1}\d{4}"])
        updates.append(["Target", True])
        updates.append(["Actual", True])

    sketch(stage, fileow, parameters, updates)

def flavor(stage, parameters):
    prompt = Label(stage, text = "Which flavor would you like to employ?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    tx = Button(stage, text = "TX", width = 10)
    tx.place(relx = 0.5, x = -62, y = 60, anchor = "n")

    tx.config(command = lambda : flavor_set(stage, parameters, "TX"))

    tx_blind = Button(stage, text = "TX Blind", width = 10)
    tx_blind.place(relx = 0.5, x = 62, y = 60, anchor = "n")

    tx_blind.config(command = lambda : flavor_set(stage, parameters, "TX Blind"))

    typology = Button(stage, text = "Typology", width = 10)
    typology.place(relx = 0.5, x = -62, y = 100, anchor = "n")

    typology.config(command = lambda : flavor_set(stage, parameters, "Typology"))

    new_typology = Button(stage, text = "New Typology", width = 10)
    new_typology.place(relx = 0.5, x = 62, y = 100, anchor = "n")

    new_typology.config(command = lambda : flavor_set(stage, parameters, "New Typology"))

    itold = Button(stage, text = "ITOLD", width = 10)
    itold.place(relx = 0.5, x = -62, y = 140, anchor = "n")

    itold.config(command = lambda : flavor_set(stage, parameters, "ITOLD"))

    ncjc = Button(stage, text = "NCJC", width = 10)
    ncjc.place(relx = 0.5, x = 62, y = 140, anchor = "n")

    ncjc.config(command = lambda : flavor_set(stage, parameters, "NCJC"))

    custom = Button(stage, text = "Custom", width = 20)
    custom.place(relx = 0.5, x = 0, y = 180, anchor = "n")

    custom.config(command = lambda : sketch(stage, test, parameters, None))

def defvals_set(stage, parameters):
    updates = []

    updates.append(["Phase Regex", r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"])
    updates.append(["Participant Regex", r"\w\d\d\d"])
    updates.append(["Target", True])
    updates.append(["Actual", True])
    updates.append(["Overwrite", True])
    updates.append(["Blank Repeated Labels", True])

    sketch(stage, proceed, parameters, updates)

def defvals(stage, parameters):
    prompt = Label(stage, text = "Would you like to run the default values?")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    yes = Button(stage, text = "Yes", width = 5)
    yes.place(relx = 0.5, x = -40, y = 60, anchor = "n")

    yes.config(command = lambda : defvals_set(stage, parameters))

    no = Button(stage, text = "No", width = 5)
    no.place(relx = 0.5, x = 40, y = 60, anchor = "n")

    no.config(command = lambda : sketch(stage, flavor, parameters, None))

def query_input(stage, parameters, entry):
    updates = []

    if entry:
        updates.append(["Query", entry])
        sketch(stage, defvals, parameters, updates)
    else:
        sketch(stage, query, parameters, updates)

def query(stage, parameters):
    querytext = StringVar()

    prompt = Label(stage, text = "Please input the name of the query")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    entry = Entry(stage, textvariable = querytext)
    entry.place(relx = 0.5, x = 0, y = 50, anchor = "n")

    submit = Button(stage, text = "Submit", width = 5)
    submit.place(relx = 0.5, x = 0, y = 90, anchor = "n")

    submit.config(command = lambda : query_input(stage, parameters, querytext.get()))

def fp_select(stage, parameters):
    updates = []

    dir = dialog.askdirectory(initialdir = "/", title = "Select a Directory")

    if dir:
        updates.append(["Directory", dir])
        sketch(stage, query, parameters, updates)
    else:
        sketch(stage, fp, parameters, updates)

def fp(stage, parameters):
    prompt = Label(stage, text = "Please choose the directory of analysis")
    prompt.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    browse = Button(stage, text = "Browse Directories", width = 20)
    browse.place(relx = 0.5, x = 0, y = 60, anchor = "n")

    browse.config(command = lambda : fp_select(stage, parameters))

def start(stage, parameters):
    start = Button(stage, text = "Start", width = 5)
    start.place(relx = 0.5, x = 0, y = 320, anchor = "s")
    
    start.config(command = lambda : sketch(stage, fp, parameters, None))

def sketch(stage, scene, parameters, updates):
    if updates:
        for update in updates:
            parameters[update[0]] = update[1]

    for widget in stage.winfo_children():
        widget.destroy()

    scene(stage, parameters)

if __name__ == "__main__":
    parameters = {
        "Directory" : None,
        "Query" : None,
        "Phase Regex" : None,
        "Participant Regex" : None,
        "Target" : None,
        "Actual" : None,
        "Overwrite" : None,
        "Blank Repeated Labels" : None
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

    sketch(stage, start, parameters, None)

    root.mainloop()  # Keeps the window open
