import tkinter as tk

from tkinter import Tk

from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Combobox
from tkinter.ttk import Checkbutton
from tkinter.ttk import Progressbar

from tkinter import font
from tkinter import filedialog as dialog
from tkinter import messagebox as mbox

from tkinter import StringVar
from tkinter import BooleanVar

from os.path import isdir

import threading
import queue
import logging
import time  # TEMP

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
from phon_query_to_csv.create_pivot_table import create_pivot_table
# from phon_query_to_csv.column_match import column_match # Optional

log = setup_logging(logging.INFO, __name__)

"""
Analysis Progress

create_pivot_table {
    Selections

    Which variable do you want to group by? (Multiple selections) {
        Date, Record, Group, Tier, Range, IPA Target, IPA Actual, Alignment, Result, filename, Query Source, Analysis, Phase, Language, Participant, Speaker, Probe, Probe Type, IPA Alignment, Tiers, Notes, Orthography, IPA Target Words, IPA Actual Words, IPA Alignment Words, Accuracy, Deletion, Substitution, ID-Actual-Lang, Actual Num Segs, A1, A1_Base, A1_voice, A1_place, A1_manner, A1_sonority, A1_EML, A2, A2_Base, A2_voice, A2_place, A2_manner, A2_sonority, A2_EML, A3, A3_Base, A3_voice, A3_place, A3_manner, A3_sonority, A3_EML, ID-Target-Lang, Target Type, Target Num Segs, T1, T1_Base, T1_voice, T1_place, T1_manner, T1_sonority, T1_EML, T2, T2_Base, T2_voice, T2_place, T2_manner, T2_sonority, T2_EML, T3, T3_Base, T3_voice, T3_place, T3_manner, T3_sonority, T3_EML
    
        Default : Participant, Phase, Language, Analysis, IPA Target
    }

    Which value(s) do you want to filter [VARIABLE] by? (N times for every variable; multiple selections) {
        Varies
    }

    Which would you like to be your values? (Only one) {
        Date, Record, Group, Tier, Range, IPA Actual, Alignment, Result, filename, Query Source, Speaker, Probe, Probe Type, IPA Alignment, Tiers, Notes, Orthography, IPA Target Words, IPA Actual Words, IPA Alignment Words, Accuracy, Deletion, Substitution, ID-Actual-Lang, Actual Num Segs, A1, A1_Base, A1_voice, A1_place, A1_manner, A1_sonority, A1_EML, A2, A2_Base, A2_voice, A2_place, A2_manner, A2_sonority, A2_EML, A3, A3_Base, A3_voice, A3_place, A3_manner, A3_sonority, A3_EML, ID-Target-Lang, Target Type, Target Num Segs, T1, T1_Base, T1_voice, T1_place, T1_manner, T1_sonority, T1_EML, T2, T2_Base, T2_voice, T2_place, T2_manner, T2_sonority, T2_EML, T3, T3_Base, T3_voice, T3_place, T3_manner, T3_sonority, T3_EML
    }

    Which aggregation function would you like to apply? (If value numerical) {
        mean, sum, count, min, max, median, std

        Default : mean
    }
}

Program completion message {
    Pivot Table Created
    
    The output file is located at the following directory:
    [DIRECTORY]
    
    Below is a preview of the pivot table:
    [SLICE]

    You may now quit the program.
}

"""

def run(layers, parameters, setting):
    def update():
        try:
            while True:
                value, label = event_queue.get_nowait()

                state["target"] = value
                state["label"] = label
                
        except queue.Empty:
            pass

        current = widgets["Progressbar"]["Progress"]["value"]
        target = state["target"]

        distance = target - current

        if distance > 0.5:
            step = distance * 0.1
            widgets["Progressbar"]["Progress"]["value"] = current + step
        else:
            widgets["Progressbar"]["Progress"]["value"] = target

        widgets["Label"]["Status"]["text"] = state.get("label", widgets["Label"]["Status"]["text"])

        setting.after(30, update)

    def analyze():
        steps = [(10.0, "Generating CSV files..."), 
                (20.0, "Merging CSV files..."), 
                (30.0, "Handling accuracy calculation..."), 
                (45.0, "Expanding phone data..."), 
                (75.0, "Creating pivot table..."), 
                (100.0, "Complete!")]

        for s in range(len(steps) - 1):
            event_queue.put(steps[s])

            match steps[s][1]:
                case "Generating CSV files...":
                    results["gen_csv"] = gen_csv(parameters["Directory"],
                                                parameters["Query"],
                                                parameters["Flavor"]["Phase"],
                                                parameters["Flavor"]["Participant"],
                                                overwrite = True)
                
                case "Merging CSV files...":
                    results["filepath"] = merge_csv(results["gen_csv"][0])

                case "Handling accuracy calculation...":
                    if parameters["Flavor"]["Target"]:
                        results["filepath"] = calculate_accuracy(results["filepath"])

                case "Expanding phone data...":
                    results["final"] = phone_data_expander(results["filepath"],
                                                        results["gen_csv"][0],
                                                        target = parameters["Flavor"]["Target"],
                                                        actual = parameters["Flavor"]["Actual"])
                    
                case "Creating pivot table...":
                    time.sleep(0.5) # PLACEHOLDER UNTIL PIVOT TABLE CREATION CODE COMPLETE

            event_queue.put((steps[s][0] + 1, steps[s][1]))

        event_queue.put(steps[-1])

    results = {
        "gen_csv" : None,
        "filepath" : None,
        "final" : None
    }

    widgets = {
        "Label" : {
            "Process" : Label(setting, text = ("Running Query: " + parameters["Query"])),
            "Status" : Label(setting, text = "Initializing data...", font = font.Font(size = 10))
        },
        "Progressbar" : {
            "Progress" : Progressbar(setting, orient = "horizontal", mode = "determinate", length = 320)
        }
    }

    widgets["Label"]["Process"].place(relx = 0.5, y = 0, anchor = "n")
    widgets["Label"]["Status"].place(relx = 0.5, y = 70, anchor = "n")
    widgets["Progressbar"]["Progress"].place(relx = 0.5, y = 45, anchor = "n")

    event_queue = queue.Queue()
    state = {"target" : 0, "label" : "Initializing data..."}

    analysis = threading.Thread(target = analyze, daemon = True)
    analysis.start()

    update()
    
def flavor(layers, parameters, setting):
    def transition():
        presets = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC")

        parameters["Flavor"]["Phase"] = phase.get()
        parameters["Flavor"]["Participant"] = participant.get()
        parameters["Flavor"]["Target"] = target.get()
        parameters["Flavor"]["Actual"] = actual.get()

        if parameters["Flavor"]["Name"] in presets:
            preset = preset(parameters["Flavor"]["Name"])

            matches = [parameters["Flavor"]["Phase"] == preset["Phase"], 
                    parameters["Flavor"]["Participant"] == preset["Participant"], 
                    parameters["Flavor"]["Target"] == preset["Target"], 
                    parameters["Flavor"]["Actual"] == preset["Actual"]]

            for match in matches:
                if not match:
                    mbox.showwarning(title = "Modification of preset flavor", message = "Because you modified a preset flavor, the flavor name will be changed to \"Custom\".")
                    parameters["Flavor"]["Name"] = "Custom"

                    break

        sketch(layers, parameters, "Scene", query)

    def inform():
        helptext = ("What is a regex?"
                "\n\n"
                "Regex strings are strings of text representative of a pattern of text. "
                "In this case, the regex strings match the exact phase and participant for which to search."
                "\n\n"
                "As an example, the string \"" + r"\w(?=\d{4})" + "\" would match to any string beginning with a word character followed by four digits.")
        
        mbox.showinfo(title = "Helpful Information", message = helptext)

    phase = StringVar()
    participant = StringVar()
    target = BooleanVar()
    actual = BooleanVar()

    phase.set(parameters["Flavor"]["Phase"])
    participant.set(parameters["Flavor"]["Participant"])
    target.set(parameters["Flavor"]["Target"])
    actual.set(parameters["Flavor"]["Actual"])

    widgets = {
        "Label" : {
            "Name" : Label(setting, text = ("Flavor: " + parameters["Flavor"]["Name"])),
            "Regex" : Label(setting, text = "Please specify the regex strings"),
            "Phase" : Label(setting, text = "Phase"),
            "Participant" : Label(setting, text = "Participant"),
            "Booleans" : Label(setting, text = "Please specify if Target and / or Actual should be analyzed")
        },
        "Button" : {
            "Help" : Button(setting, text = "󰋼 ", width = 3),
            "Save" : Button(setting, text = "Save", width = 5)
        },
        "Entry" : {
            "Phase" : Entry(setting, textvariable = phase, width = 25),
            "Participant" : Entry(setting, textvariable = participant, width = 25)
        },
        "Checkbutton" : {
            "Target" : Checkbutton(setting, variable = target, text = "Analyze Target"),
            "Actual" : Checkbutton(setting, variable = actual, text = "Analyze Actual")
        }
    }

    widgets["Label"]["Name"].place(relx = 0.5, x = 0, y = 0, anchor = "n")
    widgets["Label"]["Regex"].place(relx = 0.5, x = 0, y = 55, anchor = "n")
    widgets["Label"]["Phase"].place(relx = 0.5, x = -125, y = 90, anchor = "n")
    widgets["Label"]["Participant"].place(relx = 0.5, x = 125, y = 90, anchor = "n")
    widgets["Label"]["Booleans"].place(relx = 0.5, x = 0, y = 190, anchor = "n")

    widgets["Button"]["Help"].place(relx = 0.5, x = 145, y = 52, anchor = "n")
    widgets["Button"]["Save"].place(relx = 0.5, x = 0, y = 332, anchor = "s")

    widgets["Button"]["Help"].config(command = lambda : inform())
    widgets["Button"]["Save"].config(command = lambda : transition())

    widgets["Entry"]["Phase"].place(relx = 0.5, x = -125, y = 125, anchor = "n")
    widgets["Entry"]["Participant"].place(relx = 0.5, x = 125, y = 125, anchor = "n")

    widgets["Checkbutton"]["Target"].place(relx = 0.5, x = 60, y = 225, anchor = "nw")
    widgets["Checkbutton"]["Actual"].place(relx = 0.5, x = -60, y = 225, anchor = "ne")

def query(layers, parameters, setting):
    def transition(specify):
        presets = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC")

        parameters["Query"] = name.get()
        parameters["Directory"] = directory.get()
        parameters["Flavor"]["Name"] = flavor.get()

        if (parameters["Flavor"]["Name"] in presets):
            specs = preset(parameters["Flavor"]["Name"])
            
            parameters["Flavor"]["Phase"] = specs["Phase"]
            parameters["Flavor"]["Participant"] = specs["Participant"]
            parameters["Flavor"]["Target"] = specs["Target"]
            parameters["Flavor"]["Actual"] = specs["Actual"]

        parameters["Blanking"] = blanking.get()

        if specify:
            sketch(layers, parameters, "Scene", flavor)
        else:
            errormessage = "The following faulty inputs were identified:"

            if not parameters["Query"]:
                errormessage += "\n- Name"

            if not isdir(parameters["Directory"]):
                errormessage += "\n- Directory"

            if not parameters["Flavor"]["Name"] or not parameters["Flavor"]["Phase"] or not parameters["Flavor"]["Participant"]:
                errormessage += "\n- Flavor"

            if errormessage == "The following faulty inputs were identified:":
                if mbox.askyesno(title = "Confirmation", message = "Are you sure you want to run the analysis? Any existing files in the 'Compiled' directory will be overwritten"):
                    sketch(layers, parameters, "Scene", run)
            else:
                errormessage += "\n\nPlease ensure that a source label is specified, an existing directory is specified, and a flavor is selected and properly defined."
                errormessage += " You can search for an existing directory with the button next to its entry and specify a flavor with the button next to its selection."

                mbox.showerror(title = "Unable to run", message = errormessage)

    def browse():
        dir = dialog.askdirectory(initialdir = "/", title = "Select a Directory")

        if dir:
            directory.set(dir)

    boxoptions = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC", "Custom")

    name = StringVar()
    directory = StringVar()
    flavor = StringVar()
    blanking = BooleanVar()

    name.set(parameters["Query"])
    directory.set(parameters["Directory"])
    flavor.set(parameters["Flavor"]["Name"])
    blanking.set(parameters["Blanking"])

    widgets = {
        "Label" : {
            "Name" : Label(setting, text = "Please specify a label for the source / source query below"),
            "Directory" : Label(setting, text = "Please specify the directory of the source data below"),
            "Flavor" : Label(setting, text = "Please specify the flavor of the source analysis below")
        },
        "Button" : {
            "Directory" : Button(setting, text = "󰥨 ", width = 3),
            "Flavor" : Button(setting, text = "󰝰 ", width = 3),
            "Run" : Button(setting, text = "Run", width = 5)
        },
        "Entry" : {
            "Name" : Entry(setting, textvariable = name, width = 25),
            "Directory" : Entry(setting, textvariable = directory, width = 25)
        },
        "Combobox" : {
            "Flavor" : Combobox(setting, textvariable = flavor, values = boxoptions, state = "readonly", width = 23)
        },
        "Checkbutton" : {
            "Blanking" : Checkbutton(setting, variable = blanking, text = "Blank out repeated labels")
        }
    }

    widgets["Label"]["Name"].place(relx = 0.5, x = 0, y = 0, anchor = "n")
    widgets["Label"]["Directory"].place(relx = 0.5, x = 0, y = 80, anchor = "n")
    widgets["Label"]["Flavor"].place(relx = 0.5, x = 0, y = 160, anchor = "n")

    widgets["Button"]["Directory"].place(relx = 0.5, x = 130, y = 109, anchor = "n")
    widgets["Button"]["Flavor"].place(relx = 0.5, x = 130, y = 189, anchor = "n")
    widgets["Button"]["Run"].place(relx = 0.5, x = 0, y = 332, anchor = "s")

    widgets["Button"]["Directory"].config(command = lambda : browse())
    widgets["Button"]["Flavor"].config(command = lambda : transition(True))
    widgets["Button"]["Run"].config(command = lambda : transition(False))

    widgets["Entry"]["Name"].place(relx = 0.5, x = 0, y = 35, anchor = "n")
    widgets["Entry"]["Directory"].place(relx = 0.5, x = 0, y = 115, anchor = "n")

    widgets["Combobox"]["Flavor"].place(relx = 0.5, x = 0, y = 195, anchor = "n")

    widgets["Checkbutton"]["Blanking"].place(relx = 0.5, x = 0, y = 240, anchor = "n")

def backdrop(layers, parameters, setting):
    def transition():
        widgets["Button"]["Start"].destroy()

        sketch(layers, parameters, "Scene", query)

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
    
    widgets["Button"]["Start"].configure(command = lambda : transition())
    widgets["Button"]["Quit"].configure(command = lambda : root.destroy())

def preset(flavor):
    specs = {
        "Phase" : "",
        "Participant" : "",
        "Target" : False,
        "Actual" : False
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
        "Query" : "Queries_Target_v2",
        "Directory" : r"/home/fzvial/Documents/Work/CLD Lab/Phon Query Testing/Testing/full",
        "Flavor" : {
            "Name" : "TX",
            "Phase" : r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}",
            "Participant" : r"\w\d\d\d",
            "Target" : True,
            "Actual" : True
        },
        "Blanking" : True
    }

    root = Tk()

    root.title("Phon Query to CSV")
    root.geometry("800x600")

    stage = Frame(root, width = 800, height = 600)
    scene = Frame(stage, width = 680, height = 332)

    layers = {
        "Root" : root,
        "Stage" : stage,
        "Scene" : scene
    }

    font.nametofont("TkDefaultFont").configure(size = 12)

    sketch(layers, parameters, "Stage", backdrop)

    root.mainloop()

    print(parameters)

"""

Notes for improvemenet:
- Change query name to general "Please provide a label for the source / source query:"
- End goal: give user multiple ways to determine accuracy

"""
