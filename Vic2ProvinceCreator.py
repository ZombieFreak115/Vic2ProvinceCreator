import csv
import os
import re
import PySimpleGUI as sg
from collections import OrderedDict
from collections import defaultdict
def collapse(layout, key, visible):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this section visible / invisible
    :param visible: visible determines if section is rendered visible or invisible on initialization
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0,0)))


select_file_column = [
    [
        sg.Text("Select Mod dir:"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(key="-IN-"),
        sg.Button('Create Province', key="-CREATE_PROVINCE-", enable_events=True)

    ]

]

land_column = [
    [sg.Input("", key="continent_input"), sg.Text("Continent (must be the filename for it):")],
    [sg.Input("", key="climate_input"), sg.Text("Climate (must be the filename for it):")],
    [sg.Input("", key="region_input"), sg.Checkbox('Make State Capital', enable_events=True, key='state_capital_key'), sg.Text("Regions the province will be put in\na new one will be created if it doesn't exist, multiple regions can be passed by using commas(,):")],
    [sg.Input("", key="LR_input"), sg.Text("Life Rating:")],
    [sg.Input("", key="owner_input"), sg.Text("Owner (empty for uncolonized):")],
    [sg.Input("", key="controller_input"), sg.Text("Controller (empty for same as owner):")],
    [sg.Input("", key="cores_input"), sg.Text("Cores (seperate tags with comma):")],
    [sg.Input("", key="RGO_input"), sg.Text("RGO:")]
]

layout_main = [
    [
        [sg.Column(select_file_column), sg.Text("", key="-ERRORTEXT-")],
        [sg.Input("234,124,251", key="RBG_input"), sg.Text("RGB for province, with commas(,) separating the numbers:")],
        [sg.Input("", key="loc_name_input"), sg.Text("Ingame Name:")],
        [sg.Checkbox('Check if land province', enable_events=True, key='land_province_key')],
        collapse(land_column, 'hide_key', False),
        sg.VerticalSeparator(),

    ]
]

window_main = sg.Window("Vic2 Province Creator", layout_main, modal=True)

toggle_land = False

state_capital = False


while True:
    event, values = window_main.read()
    # stores the values from the filebrowse (-IN-) into the variable path for later use
    path = values["-IN-"]
    if event in (None, "Quit"):
        break
    # toggles the land-only section if checked and unchecked
    elif event == 'land_province_key':
        toggle_land = not toggle_land
        window_main['hide_key'].update(visible=toggle_land)
    # toggles the land province will be a state capital or not
    elif event == 'state_capital_key':
        state_capital = not state_capital
    elif event == '-CREATE_PROVINCE-':
        # checks if all files required exists in advance, if not, return an error
        try:
            with open(path + "/map/definition.csv", "r", newline=''):
                pass
            with open(path + "/map/continent.txt", "r", newline=''):
                pass
            with open(path + "/map/climate.txt", "r", newline=''):
                pass
            with open(path + "/map/region.txt", "r", newline=''):
                pass
            with open(path + "/map/default.map", "r", newline=''):
                pass
            with open(path + "/map/positions.txt", "r", newline=''):
                pass
        except FileNotFoundError:
            window_main["-ERRORTEXT-"].update("Failure! One or more files required not found")
            continue
        error = False
        # defines all the user-input values, only the land values if the user has checked the box
        RGB_input = values["RBG_input"]
        if re.match("^(?:(?:^|,\s*)([01]?\d\d?|2[0-4]\d|25[0-5])){3}$" ,RGB_input) is None:
            window_main["-ERRORTEXT-"].update("Failure! Invalid RGB value")
            continue
        loc_name_input = values["loc_name_input"]
        # checks if all land prov info is not invalid
        if toggle_land:
            continent_input = values["continent_input"]
            if re.match("\S+" ,continent_input) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Continent")
                continue
            climate_input = values["climate_input"]
            if re.match("\S+" ,climate_input) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Climate")
                continue
            region_input = values["region_input"].upper()
            if re.match("\S+" ,region_input) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Region")
                continue
            # split the region input into a list incase of multiple args
            region_input = region_input.split(",")
            LR_input = values["LR_input"]
            # checks if LR input is a valid number
            if re.match("\d+" ,LR_input) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Life Rating value")
                continue
            RGO_input = values["RGO_input"].lower()
            if re.match("\S+" ,RGO_input) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid RGO")
                continue
            owner_input = values["owner_input"].upper()
            if re.match("^[A-Z][A-Z][A-Z]$|^$", owner_input, flags=re.IGNORECASE) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Owner")
                continue
            controller_input = values["controller_input"].upper()
            if re.match("^[A-Z][A-Z][A-Z]$|^$", controller_input, flags=re.IGNORECASE) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid Controller")
                continue
            cores_input = values["cores_input"].upper()
            if re.match("^[0-9A-Z]{3}(,[0-9A-Z]{3})*$|^$", cores_input, flags=re.IGNORECASE) is None:
                window_main["-ERRORTEXT-"].update("Failure! Invalid tag with core")
                continue
            cores_input = cores_input.split(",")
        dictionary_list = []
        list_of_prov_ids = []
        with open(path + "/map/definition.csv", "r", newline='') as fp:
            definition_list = fp.readlines()
            definition_file = "".join(definition_list)
            csv_read = csv.DictReader(definition_list, delimiter=';')
            for i in csv_read:
                dictionary_list.append(i)
            # checks if the RGB value the user typed in already exists on a province or the provid is taken and appends all provids to a seperate list
            for i in dictionary_list:
                try:
                    list_of_prov_ids.append(int(i.get("province")))
                except ValueError:
                    window_main["-ERRORTEXT-"].update("Failure! Definition.csv has invalid entries, remove them")
                    error = True
                    break
                if RGB_input == i.get("red") + "," + i.get("green") + "," + i.get("blue"):
                    window_main["-ERRORTEXT-"].update("Failure! RGB code already taken! Type in a unused one")
                    error = True
                    break
            # if there was an error in the loop, restart from scratch
            if error:
                continue
            provid_input = max(list_of_prov_ids) + 1
            provid_input = str(provid_input)
        # checks if the inputted land prov data exists and saves variables for the edit later on in the if statement
        if toggle_land:
            with open(path + "/map/continent.txt", "r", newline='') as fp:
                continent_file = fp.read()
                selected_continent = re.search(continent_input +" = {.+?provinces = {.+?}.+?}", continent_file, flags=re.IGNORECASE|re.DOTALL)
                if selected_continent is None:
                    window_main["-ERRORTEXT-"].update("Failure! Invalid Continent")
                    continue
            with open(path + "/map/climate.txt", "r", newline='') as fp:
                climate_file = fp.read()
                selected_climate = re.findall(climate_input +" =.+?{.+?}", climate_file, flags=re.IGNORECASE|re.DOTALL)
                # error if no match in the climate file
                if len(selected_climate) == 0:
                    window_main["-ERRORTEXT-"].update("Failure! Invalid Climate")
                    continue
            # begin doing the land prov editing here
            with open(path + "/map/region.txt", "r", newline='') as fp:
                region_file = fp.read()
                for i in region_input:
                    selected_region = re.search(i +" =.+?{.+?}", region_file, flags=re.IGNORECASE|re.DOTALL)
                    # if the region already exists
                    if selected_region is not None:
                        # if the state capital checkmark is checked
                        if state_capital:
                            edited_region = re.sub("{", "{ "+ provid_input + " ", selected_region.group())
                            # copies over the changes to the main region file in memory, file is not yet overwritten
                            region_file = re.sub(selected_region.group(), edited_region, region_file)
                        else:
                            edited_region = re.sub("}", " " + provid_input + " }", selected_region.group())
                            # copies over the changes to the main region file in memory, file is not yet overwritten
                            region_file = re.sub(selected_region.group(), edited_region, region_file)
                    # if the region doesn't exist already
                    else:
                        # creates a new region entry, with the inputted region id and prov id
                        region_file = region_file + "\n" + i + " = { " + provid_input + " }"
            # Edit the continent entry
            edited_continent = re.sub("provinces =.+?{\s*", "provinces = {\n " + provid_input + " ", selected_continent.group(), flags=re.IGNORECASE|re.DOTALL)
            # copies over the changes to the main continent file in memory, file is not yet overwritten
            continent_file = re.sub(selected_continent.group(), edited_continent, continent_file)
            # Edit the climate entry
            edited_climate = re.sub("{\s*", "{\n " + provid_input + " ", selected_climate[1], flags=re.IGNORECASE|re.DOTALL)
            # copies over the changes to the main climate file in memory, file is not yet overwritten
            climate_file = re.sub(selected_climate[1], edited_climate, climate_file)
            # starts editing/creating provincefile
            if os.path.exists(path + "/history/provinces/automadeprovinces") is False:
                os.mkdir(path + "/history/provinces/automadeprovinces")
            if "" not in cores_input:
                with open(path + "/history/provinces/automadeprovinces/" + provid_input + " - " + loc_name_input + ".txt", 'a') as f:
                    # checks for the history file if the user has input any cores
                    if controller_input == "" and owner_input == "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\n")
                    elif controller_input == "" and owner_input != "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\nowner = " + owner_input + "\ncontroller = " + owner_input + "\n")
                    elif controller_input != "" and owner_input != "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\nowner = " + owner_input + "\ncontroller = " + controller_input + "\n")
                    elif controller_input != "" and owner_input == "" :
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\n")
                    for i in cores_input:
                        f.write("add_core = " + i + "\n")
            else:
                with open(path + "/history/provinces/automadeprovinces/" + provid_input + " - " + loc_name_input + ".txt", 'w') as f:
                    # checks for the history file if the user havent input any cores
                    if controller_input == "" and owner_input == "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\n")
                    elif controller_input == "" and owner_input != "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\nowner = " + owner_input + "\ncontroller = " + owner_input + "\n")
                    elif controller_input != "" and owner_input != "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\nowner = " + owner_input + "\ncontroller = " + controller_input + "\n")
                    elif controller_input != "" and owner_input == "":
                        f.write('trade_goods = ' + RGO_input + "\nlife_rating = " + LR_input + "\n")
        # append new province to definition file
        definition_file = definition_file + "\n" + provid_input + ";" + RGB_input.replace(",", ";") + ";" + loc_name_input + ";x"
        # append stuff to a new loc file
        if not os.path.exists(path + "/localisation/auto_made_provinces.csv"):
            with open(path + "/localisation/auto_made_provinces.csv", 'w') as f:
                f.write(";;;;;;;;;;;;;;x,,,")
        with open(path + "/localisation/auto_made_provinces.csv", 'a') as f:
            f.write("\n" + "PROV" + provid_input + ";" + loc_name_input + ";x")
        # write stuff to default.map file
        with open(path + "/map/default.map", 'r') as f:
            defaultmap_file = f.read()
            max_provinces_string = re.search("^max_provinces = \d+", defaultmap_file)
            max_provs_before_int = re.sub("[^0-9]", "", max_provinces_string.group())
            max_prov_int = int(provid_input) + 1
            max_provinces = str(max_prov_int)
            max_provinces_string_new = re.sub("[0-9]+", max_provinces, max_provinces_string.group())
            # do the edit in memory
            defaultmap_file = re.sub(max_provinces_string.group(), max_provinces_string_new, defaultmap_file)
            # if it isn't a land province, add it to sea_starts ( sea prov)
            if toggle_land is False:
                sea_starts = re.search("sea_starts =.+?{.+?}", defaultmap_file, flags=re.IGNORECASE|re.DOTALL)
                sea_starts_new = re.sub("{\s*", "{\n " + provid_input + " ", sea_starts.group())
                defaultmap_file = re.sub(sea_starts.group(), sea_starts_new, defaultmap_file)
        # overwrite files in mod dir with edited strings
        with open(path + "/map/definition.csv", "w", newline='') as fp:
            fp.write(definition_file)
        if toggle_land:
            with open(path + "/map/continent.txt", "w", newline='') as fp:
                fp.write(continent_file)
            with open(path + "/map/climate.txt", "w", newline='') as fp:
                fp.write(climate_file)
            with open(path + "/map/region.txt", "w", newline='') as fp:
                fp.write(region_file)
        with open(path + "/map/default.map", "w", newline='') as fp:
            fp.write(defaultmap_file)
        with open(path + "/map/positions.txt", "a", newline='') as fp:
            fp.write("\n" + provid_input + " = {\n\n}")
        window_main["-ERRORTEXT-"].update("Province Created Successfully!")

# make sure the checks disallow empty ("") strings
# check if it really CAN detect duplicate RGB values
# make RGO value always lowercase
# make region value always uppercase when created, and check it can create new regions without problems (with commas)
# Make it handle the "empty" definition entries that can cause it to fuk up