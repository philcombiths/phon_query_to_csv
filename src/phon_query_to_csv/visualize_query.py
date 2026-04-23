from tkinter import Tk

from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Combobox
from tkinter.ttk import Checkbutton
from tkinter.ttk import Progressbar
from tkinter.ttk import Scrollbar

from tkinter import Listbox

from tkinter import font
from tkinter import filedialog as dialog
from tkinter import messagebox as mbox

from tkinter import StringVar
from tkinter import BooleanVar

from os.path import isdir

import threading
import queue
import os
import pandas as pd

from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
from phon_query_to_csv.create_pivot_table import create_pivot_table

def pivot(parameters, setting):
    finished = BooleanVar(value = False)

    def transition():
        errormessage = ("Please check that variables have been chosen and each have at least one allowed value, "
                        "that there is a variable chosen for the table values, "
                        "and that there is an aggregation function selected.")

        args["Values"] = widgets["Combobox"]["Value"].get()
        args["Aggfunc"] = widgets["Combobox"]["Aggregation"].get().lower()

        valid = True

        for variable in args["Index"].keys():
            for unique in args["Index"][variable].keys():
                valid = args["Index"][variable][unique]

                if valid:
                    break

            if not valid:
                break

        valid = valid and args["Values"] and args["Aggfunc"]
        
        if not valid:
            mbox.showerror(title = "Unable to create the pivot table", message = errormessage)
        else:
            finished.set(True)

            for category in widgets.keys():
                for widget in widgets[category].keys():
                    widgets[category][widget].place_forget()

    def inform():
        helptext = ("Creating the pivot table"
                    "\n\n"
                    "The leftmost box contains options for possible variables. "
                    "Those that are selected can have filters applied to them by choosing an individual variable in the center top drop-down box and selecting unique values in the rightmost box. "
                    "\n\n"
                    "Below the previously mentioned drop-down box, two other drop-down boxes contain options for the values of the pivot table as well as the aggregation funciton to apply. "
                    "Any values variable that is already selected in the leftmost box will not appear in the drop-down, so to select it for the values, you must deselect it from the leftmost box. "
                    "\n\n"
                    "To see this helpful information again, click the info button next to the prompt.")
        
        mbox.showinfo(title = "Helpful Information", message = helptext)

    def handle_filters(event):
        selections = [widgets["Listbox"]["Filters"].get(s) for s in widgets["Listbox"]["Filters"].curselection()]
        variable = widgets["Combobox"]["Filterable"].get()

        for selection in selections:
            args["Index"][variable][selection] = True

        for filter in list(args["Index"][variable].keys()):
            if filter not in selections:
                args["Index"][variable][filter] = False

    def handle_filterable(event):
        variable = widgets["Combobox"]["Filterable"].get()

        widgets["Listbox"]["Filters"].delete(0, "end")

        if variable:
            for value in args["Index"][variable].keys():
                widgets["Listbox"]["Filters"].insert("end", value)

                if args["Index"][variable].get(value):
                    widgets["Listbox"]["Filters"].selection_set("end")

    def handle_variables(event):
        selections = [widgets["Listbox"]["Variables"].get(s) for s in widgets["Listbox"]["Variables"].curselection()]

        for selection in selections:
            if selection not in args["Index"].keys():
                args["Index"][selection] = {}

                for value in sorted(df[selection].dropna().unique()):
                    args["Index"][selection][str(value)] = True

        for variable in list(args["Index"].keys()):
            if variable not in selections:
                args["Index"].pop(variable, None)

        widgets["Combobox"]["Filterable"].configure(values = selections)

        if widgets["Combobox"]["Filterable"].get() not in selections:
            widgets["Combobox"]["Filterable"].set("")

            widgets["Listbox"]["Filters"].delete(0, "end")

        values = []

        for value in df.columns:
            if value not in selections and pd.api.types.is_numeric_dtype(df[value]):
                values.append(value)

        widgets["Combobox"]["Value"].configure(values = values)

        if widgets["Combobox"]["Value"].get() in selections:
            widgets["Combobox"]["Value"].set("")

    args = {
        "Index" : {},
        "Values" : None,
        "Aggfunc" : None
    }

    fp = os.path.join(parameters["gen_csv"][0], 'Compiled', 'merged_files', 'full_annotated_dataset.csv')

    df = pd.read_csv(fp, encoding = 'utf-8')

    values = []
    defaults = ['Participant', 'Phase', 'Language', 'Analysis', 'IPA Target']

    for value in df.columns:
        if pd.api.types.is_numeric_dtype(df[value]):
            values.append(value)

    aggfuncs = ["Mean", "Sum", "Count", "Min", "Max", "Median", "STD"]

    widgets = {
        "Label" : {
            "Prompt" : Label(setting, text = "Select variables and their filters, and values and their aggregation     󰋼 "),
            "ArrowOne" : Label(setting, text = "󰜴 ", font = font.Font(size = 14)),
            "ArrowTwo" : Label(setting, text = "󰜴 ", font = font.Font(size = 14)),
            "Divider" : Label(setting, text = "󰇘 󰇘 󰇘 󰇘 󰇘 ", font = font.Font(size = 14))
        },
        "Button" : {
            "Help" : Button(setting, text = "󰋼 ", width = 3),
            "Finish" : Button(setting, text = "Finish", width = 5)
        },
        "Listbox" : {
            "Variables" : Listbox(setting, width = 20, height = 6, selectmode = "multiple", exportselection = False),
            "Filters" : Listbox(setting, width = 20, height = 6, selectmode = "multiple", exportselection = False)
        },
        "Scrollbar" : {
            "Variables" : Scrollbar(setting, orient = "vertical"),
            "Filters" : Scrollbar(setting, orient = "vertical")
        },
        "Combobox" : {
            "Filterable" : Combobox(setting, width = 20),
            "Value" : Combobox(setting, width = 20, values = values),
            "Aggregation" : Combobox(setting, width = 20, values = aggfuncs)
        }
    }

    widgets["Label"]["Prompt"].place(relx = 0.5, y = 115, anchor = "n")
    widgets["Label"]["ArrowOne"].place(relx = 0.5, x = -115, y = 153, anchor = "n")
    widgets["Label"]["ArrowTwo"].place(relx = 0.5, x = 115, y = 153, anchor = "n")
    widgets["Label"]["Divider"].place(relx = 0.5, y = 180, anchor = "n")

    widgets["Button"]["Help"].place(relx = 0.5, x = 264, y = 111, anchor = "n")
    widgets["Button"]["Finish"].place(relx = 0.5, x = 0, y = 332, anchor = "s")

    widgets["Button"]["Help"].configure(command = lambda : inform())
    widgets["Button"]["Finish"].configure(command = lambda : transition())

    widgets["Listbox"]["Variables"].place(relx = 0.5, x = -220, y = 155, anchor = "n")
    widgets["Listbox"]["Filters"].place(relx = 0.5, x = 220, y = 155, anchor = "n")

    for variable in df.columns:
        widgets["Listbox"]["Variables"].insert("end", variable)

        if variable in defaults:
            widgets["Listbox"]["Variables"].selection_set("end")

    handle_variables(None)

    widgets["Listbox"]["Variables"].configure(font = font.Font(size = 10))
    widgets["Listbox"]["Filters"].configure(font = font.Font(size = 10))

    widgets["Listbox"]["Variables"].configure(yscrollcommand = widgets["Scrollbar"]["Variables"].set)
    widgets["Listbox"]["Filters"].configure(yscrollcommand = widgets["Scrollbar"]["Filters"].set)

    widgets["Listbox"]["Variables"].bind("<<ListboxSelect>>", handle_variables)
    widgets["Listbox"]["Filters"].bind("<<ListboxSelect>>", handle_filters)

    widgets["Scrollbar"]["Variables"].place(relx = 0.5, x = -147, y = 157, anchor = "n", height = 120)
    widgets["Scrollbar"]["Filters"].place(relx = 0.5, x = 292, y = 157, anchor = "n", height = 120)

    widgets["Scrollbar"]["Variables"].configure(command = widgets["Listbox"]["Variables"].yview)
    widgets["Scrollbar"]["Filters"].configure(command = widgets["Listbox"]["Filters"].yview)

    widgets["Combobox"]["Filterable"].place(relx = 0.5, y = 155, anchor = "n")
    widgets["Combobox"]["Value"].place(relx = 0.5, y = 215, anchor = "n")
    widgets["Combobox"]["Aggregation"].place(relx = 0.5, y = 255, anchor = "n")

    widgets["Combobox"]["Filterable"].configure(state = "readonly")
    widgets["Combobox"]["Value"].configure(state = "readonly")
    widgets["Combobox"]["Aggregation"].configure(state = "readonly")

    widgets["Combobox"]["Filterable"].bind("<<ComboboxSelected>>", handle_filterable)

    inform()

    while not finished.get():
        continue

    return df, args

def run(layers, parameters, setting):
    def finish():
        widgets["Label"]["Close"].place(relx = 0.5, y = 165, anchor = "n")

        widgets["Label"]["Close"].configure(font = font.Font(size = 16, weight = font.BOLD), justify = "center")

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
            step = distance * 0.05
            widgets["Progressbar"]["Progress"]["value"] = current + step
        else:
            widgets["Progressbar"]["Progress"]["value"] = target

        widgets["Label"]["Status"]["text"] = state.get("label", widgets["Label"]["Status"]["text"])

        setting.after(30, update)

    def analyze():
        steps = [(10.0, "Generating CSV files..."), 
                 (20.0, "Merging CSV files..."), 
                 (30.0, "Handling accuracy calculation..."), 
                 (65.0, "Expanding phone data..."), 
                 (95.0, "Creating pivot table..."), 
                 (100.0, "Complete!")]

        for s in range(len(steps) - 1):
            event_queue.put(steps[s])

            if steps[s][1] == "Generating CSV files...":
                results["gen_csv"] = gen_csv(parameters["Directory"],
                                             parameters["Query"],
                                             parameters["Flavor"]["Phase"],
                                             parameters["Flavor"]["Participant"],
                                             overwrite = True)
                
            if steps[s][1] ==  "Merging CSV files...":
                results["filepath"] = merge_csv(results["gen_csv"][0])

            if steps[s][1] ==  "Handling accuracy calculation...":
                if parameters["Flavor"]["Target"]:
                    results["filepath"] = calculate_accuracy(results["filepath"])

            if steps[s][1] ==  "Expanding phone data...":
                results["final"] = phone_data_expander(results["filepath"],
                                                       results["gen_csv"][0],
                                                       target = parameters["Flavor"]["Target"],
                                                       actual = parameters["Flavor"]["Actual"])
                
            if steps[s][1] ==  "Creating pivot table...":
                df, specs = pivot(results, setting)

                results["final"] = create_pivot_table(results["gen_csv"][0], df, specs, parameters["Blanking"])

                finish()

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
            "Status" : Label(setting, text = "Initializing data...", font = font.Font(size = 10)),
            "Close" : Label(setting, text = "All output files have been successfully created.\nYou may now quit the program.")
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

def visualize_query(parameters):
    root = Tk()

    root.title("Phon Query to CSV")
    root.geometry("800x600")

    stage = Frame(root, width = 800, height = 600)
    scene = Frame(stage, width = 680, height = 332, relief = "solid", borderwidth = 1)

    layers = {
        "Root" : root,
        "Stage" : stage,
        "Scene" : scene
    }

    font.nametofont("TkDefaultFont").configure(size = 12)

    sketch(layers, parameters, "Stage", backdrop)

    root.mainloop()

    return

"""

Notes for improvemenet:
- End goal: give user multiple ways to determine accuracy

"""
