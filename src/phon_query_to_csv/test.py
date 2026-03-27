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

def test(stage, parameters):
    text = Label(stage, text = "Test!")
    text.place(relx = 0.5, x = 0, y = 20, anchor = "center")

    print(parameters)

def prop_flavor(layers, setting):

    """
    What is a Flavor?

    The flavor of analysis determines what kind of data is analyzed. A flavor is composed of four parts, 
    namely two regex strings, one for the phase and another for the participant, and two booleans, one for
    the target and another for the actual. A regex (regular expression) is a string of text that represents
    a (usually recurring) pattern of text found with other strings of text it may refer to. A boolean is
    a true-or-false value. In this case, the regex strings are meant for identifying the exact phase and
    participant to analyze, and the booleans are meant for specifying which sets of phonetic data are of
    concern.

    [IF NOT A CUSTOM FLAVOR]
    The following details specifications of the currently selected flavor:

    - Name: [Name]
    - Phase Regex: [Phase Regex]
    - Participant Regex: [Participant Regex]
    - Target: [Target]
    - Actual: [Actual]
    """

def scene_query_getinfo(layers, setting, flavor):
    specs = {
        "Phase Regex" : None,
        "Participant Regex" : None,
        "Target" : None,
        "Actual" : None
    }

    if flavor == "TX":
        specs["Phase Regex"] = r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"
        specs["Participant Regex"] = r"\w\d\d\d"
        specs["Target"] = True
        specs["Actual"] = True

    if flavor == "TX Blind":
        specs["Phase Regex"] = r"\w{1}\d{4}"
        specs["Participant Regex"] = r"\w(?=\d{4})"
        specs["Target"] = True
        specs["Actual"] = True

    if flavor == "Typology":
        specs["Phase Regex"] = r"p[IVX]+"
        specs["Participant Regex"] = r"\d\d\d"
        specs["Target"] = False
        specs["Actual"] = True

    if flavor == "New Typology":
        specs["Phase Regex"] = r"no phases"
        specs["Participant Regex"] = r"\w{3,4}\d\d"
        specs["Target"] = False
        specs["Actual"] = True

    if flavor == "ITOLD":
        specs["Phase Regex"] = r"no phases"
        specs["Participant Regex"] = r"\w{4}\d{2}"
        specs["Target"] = True
        specs["Actual"] = True

    if flavor == "NCJC":
        specs["Phase Regex"] = r"Timepoint\d|Pre|Post|Fall|Spring|Winter|Summer"
        specs["Participant Regex"] = r"\w{1}\d{4}"
        specs["Target"] = True
        specs["Actual"] = True

    sketch(layers, "None > Prop", prop_flavor)

def scene_query_setdir(entry):
    dir = dialog.askdirectory(initialdir = "/", title = "Select a Directory")

    if dir:
        entry.delete(0, "end")
        entry.insert(0, dir)

def scene_query(layers, setting):
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
            "Name" : Entry(setting, width = 25),
            "Directory" : Entry(setting, width = 25)
        },
        "Combobox" : {
            "Flavor" : Combobox(setting, values = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC"), width = 23)
        },
        "Checkbutton" : {
            "Overwrite" : Checkbutton(setting, text = "Overwrite existing files"),
            "Blanking" : Checkbutton(setting, text = "Blank out repeated labels")
        }
    }

    infotext = ("What is a Flavor?\n\n"
                "The flavor of analysis determines what kind of data is analyzed. "
                "A flavor is composed of four parts, namely two regex strings, one for the phase and another for the participant, "
                "and two booleans, one for the target and another for the actual. "
                "A regex (regular expression) is a string of text that represents a (usually recurring) pattern of text found with other strings of text it may refer to. "
                "A boolean is a true-or-false value.\n\n"
                "In this case, the regex strings are meant for identifying the exact phase and participant to analyze, "
                "and the booleans are meant for specifying which sets of phonetic data are of concern.")

    widgets["Label"]["Name"].place(relx = 0.5, x = 0, y = 0, anchor = "n")
    widgets["Label"]["Directory"].place(relx = 0.5, x = 0, y = 80, anchor = "n")
    widgets["Label"]["Flavor"].place(relx = 0.5, x = 0, y = 160, anchor = "n")

    widgets["Button"]["Directory"].place(relx = 0.5, x = 130, y = 109, anchor = "n")
    widgets["Button"]["Flavor"].place(relx = 0.5, x = 130, y = 189, anchor = "n")
    widgets["Button"]["Proceed"].place(relx = 0.5, x = 0, y = 332, anchor = "s")

    widgets["Button"]["Directory"].config(command = lambda : scene_query_setdir(widgets["Entry"]["Directory"]))
    widgets["Button"]["Flavor"].config(command = lambda : mbox.showinfo(title = "Helpful Information", message = infotext))
    widgets["Button"]["Proceed"].config(command = lambda : sketch(layers, "None > Prop", test))

    widgets["Entry"]["Name"].place(relx = 0.5, x = 0, y = 35, anchor = "n")
    widgets["Entry"]["Directory"].place(relx = 0.5, x = 0, y = 115, anchor = "n")

    widgets["Combobox"]["Flavor"].place(relx = 0.5, x = 0, y = 195, anchor = "n")

    widgets["Checkbutton"]["Overwrite"].place(relx = 0.5, x = 40, y = 240, anchor = "nw")
    widgets["Checkbutton"]["Blanking"].place(relx = 0.5, x = -40, y = 240, anchor = "ne")   

def stage_backdrop_transition(layers, button):
    button.destroy()

    sketch(layers, "None > Scene", scene_query)

def stage_backdrop(layers, setting):
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
    
    widgets["Button"]["Start"].config(command = lambda : stage_backdrop_transition(layers, widgets["Button"]["Start"]))
    widgets["Button"]["Quit"].configure(command = lambda : root.destroy())

def sketch(layers, transition, structure):
    prev, next = transition.split(" > ")

    if prev in layers.keys():
        setting = layers[prev]

        for widget in setting.winfo_children():
            widget.place_forget()

    if next in layers.keys():
        setting = layers[next]

        if next == "Stage":
            setting.place(relx = 0.5, rely = 0, x = 0, y = 0, anchor = "n")
            setting.lift()

        if next == "Scene":
            setting.place(relx = 0.5, rely = 0, x = 0, y = 180, anchor = "n")
            setting.lift()

        if next == "Prop":
            setting.place(relx = 0.5, rely = 0, x = 0, y = 20, anchor = "n")
            setting.lift()

        structure(layers, setting)

if __name__ == "__main__":
    parameters = {
        "Query" : None,
        "Directory" : None,
        "Flavor" : {
            "Name" : None,
            "Phase Regex" : None,
            "Participant Regex" : None,
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
    prop = Frame(scene, width = 600, height = 280, borderwidth = 5, relief = "solid")

    layers = {
        "Root" : root,
        "Stage" : stage,
        "Scene" : scene,
        "Prop" : prop
    }

    font.nametofont("TkDefaultFont").configure(size = 12)

    sketch(layers, "None > Stage", stage_backdrop)

    root.mainloop()  # Keeps the window open

    print(parameters)

"""

Notes for improvemenet:
- Specify technical details (e.g. what "regex" means, what files to look for in a directory)
- End goal: give user multiple ways to determine accuracy

"""
