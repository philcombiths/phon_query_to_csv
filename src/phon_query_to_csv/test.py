import tkinter as tk

from tkinter import Tk

from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Combobox
from tkinter.ttk import Scrollbar
from tkinter.ttk import Checkbutton

from tkinter import font
from tkinter import filedialog as dialog

def test(stage, parameters):
    text = Label(stage, text = "Test!")
    text.place(relx = 0.5, x = 0, y = 20, anchor = "center")

    print(parameters)

def flavorcheck(layers, parameters, setting):
    canvas = tk.Canvas(setting)
    v_scroll = Scrollbar(setting, orient = "vertical", command = canvas.yview)

    canvas.configure(yscrollcommand = v_scroll.set)

    canvas.pack(side = "left", fill = "both", expand = True)
    v_scroll.pack(side = "right", fill = "y")
    
    prompt_pha = Label(canvas, text = parameters["Phase Regex"])
    prompt_pha.place(relx = 0.5, x = 0, y = 20, anchor = "n")

    prompt_par = Label(canvas, text = parameters["Participant Regex"])
    prompt_par.place(relx = 0.5, x = 0, y = 100, anchor = "n")

    prompt_act = Label(canvas, text = parameters["Target"])
    prompt_act.place(relx = 0.5, x = 0, y = 180, anchor = "n")

    prompt_tar = Label(canvas, text = parameters["Actual"])
    prompt_tar.place(relx = 0.5, x = 0, y = 300, anchor = "n")

def query_setdir(parameters, entry):
    dir = dialog.askdirectory(initialdir = "/", title = "Select a Directory")

    if dir:
        entry.delete(0, "end")
        entry.insert(0, dir)

def query(layers, parameters, setting):
    flavors = ("TX", "TX Blind", "Typology", "New Typology", "ITOLD", "NCJC")

    name_prompt = Label(setting, text = "Please specify the name of the query below")
    name_prompt.place(relx = 0.5, x = 0, y = 0, anchor = "n")

    name = Entry(setting, width = 25)
    name.place(relx = 0.5, x = 0, y = 40, anchor = "n")

    directory_prompt = Label(setting, text = "Please specify the directory of the query below")
    directory_prompt.place(relx = 0.5, x = 0, y = 100, anchor = "n")

    directory = Entry(setting, width = 25)
    directory.place(relx = 0.5, x = 0, y = 140, anchor = "n")

    browser = Button(setting, text = "󰝰 ", width = 3)
    browser.place(relx = 0.5, x = 130, y = 134, anchor = "n")

    browser.config(command = lambda : query_setdir(parameters, directory))

    flavor_prompt = Label(setting, text = "Please specify the flavor of the query below")
    flavor_prompt.place(relx = 0.5, x = 0, y = 200, anchor = "n")

    flavor = Combobox(setting, values = flavors, width = 23)
    flavor.place(relx = 0.5, x = 0, y = 240, anchor = "n")

    details = Button(setting, text = "󰋼 ", width = 3)
    details.place(relx = 0.5, x = 130, y = 234, anchor = "n")

    details.config(command = lambda : sketch(layers, "None > Prop", flavorcheck, parameters, None))

    proceed = Button(setting, text = "Proceed")
    proceed.place(relx = 0.5, x = 0, y = 332, anchor = "s")

    proceed.config(command = lambda : sketch(layers, "None > Prop", flavorcheck, parameters, None))

def backdrop_transition(layers, parameters, button):
    button.destroy()

    sketch(layers, "None > Scene", query, parameters, None)

def backdrop(layers, parameters, setting):
    root = layers["Root"]

    title = Label(setting, text = "Phon Query to CSV")
    title.place(relx = 0.5, x = 0, y = 60, anchor = "n")

    title.configure(font = font.Font(size = 32, weight = font.BOLD, underline = 1))

    subtitle = Label(setting, text = "A Visual Interface Assistance")
    subtitle.place(relx = 0.5, x = 0, y = 120, anchor = "n")

    subtitle.configure(font = font.Font(size = 20, weight = font.BOLD))

    start = Button(setting, text = "Start", width = 5)
    start.place(relx = 0.5, x = 0, y = 478, anchor = "n")
    
    start.config(command = lambda : backdrop_transition(layers, parameters, start))

    quit = Button(setting, text = "Quit", width = 5)
    quit.place(relx = 0.5, x = 0, y = 520, anchor = "n")

    quit.configure(command = lambda : root.destroy())

def sketch(layers, transition, scene, parameters, updates):
    prev, next = transition.split(" > ")

    if updates:
        for update in updates:
            parameters[update[0]] = update[1]

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

        scene(layers, parameters, setting)

if __name__ == "__main__":
    parameters = {
        "Query" : None,
        "Directory" : None,
        "Flavor" : None,
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

    sketch(layers, "None > Stage", backdrop, parameters, None)

    root.mainloop()  # Keeps the window open

    print(parameters)

"""

Notes for improvemenet:
- Specify technical details (e.g. what "regex" means, what files to look for in a directory)
- End goal: give user multiple ways to determine accuracy

"""
