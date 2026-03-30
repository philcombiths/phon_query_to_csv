import tkinter as tk

from tkinter import Tk

from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Combobox
from tkinter.ttk import Checkbutton

from tkinter import font
from tkinter import filedialog as dialog
from tkinter import messagebox as mbox

from tkinter import StringVar
from tkinter import BooleanVar

def check(layers, parameters, setting):
    return
    
def specify(layers, parameters, setting):
    return

def query_getspecs(flavor):
    specs = {
        "Phase" : None,
        "Participant" : None,
        "Target" : None,
        "Actual" : None
    }

    if flavor == "TX":
        specs["Phase"] = r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"
        specs["Participant"] = r"\w\d\d\d"
        specs["Target"] = True
        specs["Actual"] = False

    if flavor == "TX Blind":
        specs["Phase"] = r"\w{1}\d{4}"
        specs["Participant"] = r"\w(?=\d{4})"
        specs["Target"] = True
        specs["Actual"] = True

    if flavor == "Typology":
        specs["Phase"] = r"p[IVX]+"
        specs["Participant"] = r"\d\d\d"
        specs["Target"] = False
        specs["Actual"] = True

    if flavor == "New Typology":
        specs["Phase"] = r"no phases"
        specs["Participant"] = r"\w{3,4}\d\d"
        specs["Target"] = False
        specs["Actual"] = True

    if flavor == "ITOLD":
        specs["Phase"] = r"no phases"
        specs["Participant"] = r"\w{4}\d{2}"
        specs["Target"] = True
        specs["Actual"] = True

    if flavor == "NCJC":
        specs["Phase"] = r"Timepoint\d|Pre|Post|Fall|Spring|Winter|Summer"
        specs["Participant"] = r"\w{1}\d{4}"
        specs["Target"] = True
        specs["Actual"] = True

    return specs

def query_transition(layers, parameters, updates):
    parameters["Query"] = updates[0].get()
    parameters["Directory"] = updates[1].get()
    parameters["Flavor"]["Name"] = updates[2].get()
    parameters["Overwrite"] = updates[3].get()
    parameters["Blanking"] = updates[4].get()

    presets = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC")

    if parameters["Flavor"]["Name"] in presets:
        specs = query_getspecs(parameters["Flavor"]["Name"])

        parameters["Flavor"]["Phase"] = specs["Phase"]
        parameters["Flavor"]["Participant"] = specs["Participant"]
        parameters["Flavor"]["Target"] = specs["Target"]
        parameters["Flavor"]["Actual"] = specs["Actual"]

        sketch(layers, parameters, "Scene", check)
    else:
        sketch(layers, parameters, "Scene", specify)

def query_getinfo(flavor):
    presets = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC")
    
    infotext = ("What is a Flavor?"
                "\n\n"
                "The flavor of analysis is determined according to two regex strings (for the phase and for the participant) and two booleans (for the target and for the actual). "
                "Regex strings are strings of text representative of a pattern of text, while booleans are true-or-false values. "
                "In this case, the regex strings match the exact phase and participant to search for, and the booleans specify which sets of phonetic data are of concern."
                "\n\n")
    
    if flavor in presets:
        specs = query_getspecs(flavor)

        infotext += "An example is provided for the currently selected flavor (" + flavor + ") below:"
        infotext += "\n\n"
        infotext += "- Phase: " + str(specs["Phase"])
        infotext += "\n"
        infotext += "- Participant: " + str(specs["Participant"])
        infotext += "\n"
        infotext += "- Target: " + str(specs["Target"])
        infotext += "\n"
        infotext += "- Actual: " + str(specs["Actual"])
    else:
        infotext += "To see an example, select one of the preset flavors in the dropdown box."

    mbox.showinfo(title = "Helpful Information", message = infotext)

def query_setdir(entry):
    dir = dialog.askdirectory(initialdir = "/", title = "Select a Directory")

    if dir:
        entry.delete(0, "end")
        entry.insert(0, dir)

def query(layers, parameters, setting):
    name = StringVar()
    directory = StringVar()
    flavor = StringVar()
    overwrite = BooleanVar()
    blanking = BooleanVar()

    widgets = {
        "Label" : {
            "Name" : Label(setting, text = "Please specify the name of the query below"),
            "Directory" : Label(setting, text = "Please specify the directory of the query below"),
            "Flavor" : Label(setting, text = "Please specify the flavor of the query below")
        },
        "Button" : {
            "Directory" : Button(setting, text = "󰝰 ", width = 3),
            "Flavor" : Button(setting, text = "󰋼 ", width = 3),
            "Proceed" : Button(setting, text = "Proceed")
        },
        "Entry" : {
            "Name" : Entry(setting, textvariable = name, width = 25),
            "Directory" : Entry(setting, textvariable = directory, width = 25)
        },
        "Combobox" : {
            "Flavor" : Combobox(setting, textvariable = flavor, values = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC"), width = 23)
        },
        "Checkbutton" : {
            "Overwrite" : Checkbutton(setting, variable = overwrite, text = "Overwrite existing files"),
            "Blanking" : Checkbutton(setting, variable = blanking, text = "Blank out repeated labels")
        }
    }

    widgets["Label"]["Name"].place(relx = 0.5, x = 0, y = 0, anchor = "n")
    widgets["Label"]["Directory"].place(relx = 0.5, x = 0, y = 80, anchor = "n")
    widgets["Label"]["Flavor"].place(relx = 0.5, x = 0, y = 160, anchor = "n")

    widgets["Button"]["Directory"].place(relx = 0.5, x = 130, y = 109, anchor = "n")
    widgets["Button"]["Flavor"].place(relx = 0.5, x = 130, y = 189, anchor = "n")
    widgets["Button"]["Proceed"].place(relx = 0.5, x = 0, y = 332, anchor = "s")

    widgets["Button"]["Directory"].config(command = lambda : query_setdir(widgets["Entry"]["Directory"]))
    widgets["Button"]["Flavor"].config(command = lambda : query_getinfo(flavor))
    widgets["Button"]["Proceed"].config(command = lambda : query_transition(layers, parameters, [name, directory, flavor, overwrite, blanking]))

    widgets["Entry"]["Name"].place(relx = 0.5, x = 0, y = 35, anchor = "n")
    widgets["Entry"]["Directory"].place(relx = 0.5, x = 0, y = 115, anchor = "n")

    widgets["Combobox"]["Flavor"].place(relx = 0.5, x = 0, y = 195, anchor = "n")

    widgets["Checkbutton"]["Overwrite"].place(relx = 0.5, x = 40, y = 240, anchor = "nw")
    widgets["Checkbutton"]["Blanking"].place(relx = 0.5, x = -40, y = 240, anchor = "ne")   

def backdrop_transition(layers, parameters, button):
    button.destroy()

    sketch(layers, parameters, "Scene", query)

def backdrop(layers, parameters, setting):
    widgets = {
        "Label" : {
            "Title" : Label(setting, text = "Phon Query to CSV"),
            "Subtitle" : Label(setting, text = "A Visual Interface Assistance")
        },
        "Button" : {
            "Start" : Button(setting, text = "Start", width = 5),
            "Quit" : Button(setting, text = "Quit", width = 5)
        }
    }

    root = layers["Root"]

    widgets["Label"]["Title"].place(relx = 0.5, x = 0, y = 60, anchor = "n")
    widgets["Label"]["Subtitle"].place(relx = 0.5, x = 0, y = 120, anchor = "n")

    widgets["Label"]["Title"].configure(font = font.Font(size = 32, weight = font.BOLD, underline = 1))
    widgets["Label"]["Subtitle"].configure(font = font.Font(size = 20, weight = font.BOLD))

    widgets["Button"]["Start"].place(relx = 0.5, x = 0, y = 478, anchor = "n")
    widgets["Button"]["Quit"].place(relx = 0.5, x = 0, y = 520, anchor = "n")
    
    widgets["Button"]["Start"].config(command = lambda : backdrop_transition(layers, parameters, widgets["Button"]["Start"]))
    widgets["Button"]["Quit"].configure(command = lambda : root.destroy())

def sketch(layers, parameters, transition, structure):
    if transition in layers.keys():
        setting = layers[transition]

        for widget in setting.winfo_children():
            widget.place_forget()

        if transition == "Stage":
            setting.place(relx = 0.5, rely = 0, x = 0, y = 0, anchor = "n")

        if transition == "Scene":
            setting.place(relx = 0.5, rely = 0, x = 0, y = 180, anchor = "n")
            
        setting.lift()

        structure(layers, parameters, setting)

if __name__ == "__main__":
    parameters = {
        "Query" : None,
        "Directory" : None,
        "Flavor" : {
            "Name" : None,
            "Phase" : None,
            "Participant" : None,
            "Target" : None,
            "Actual" : None
        },
        "Overwrite" : None,
        "Blank Repeated Labels" : None
    }

    root = Tk()

    root.title("Phon Query to CSV")
    root.geometry("800x600")

    stage = Frame(root, width = 800, height = 600, borderwidth = 1, relief = "solid")
    scene = Frame(stage, width = 680, height = 332, borderwidth = 1, relief = "solid")

    layers = {
        "Root" : root,
        "Stage" : stage,
        "Scene" : scene
    }

    font.nametofont("TkDefaultFont").configure(size = 12)

    sketch(layers, parameters, "Stage", backdrop)

    root.mainloop()  # Keeps the window open

    print(parameters)

"""

Notes for improvemenet:
- End goal: give user multiple ways to determine accuracy

"""
