import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import fair
from fair.RCPs import rcp3pd, rcp45, rcp6, rcp85
from CreateToolTip import *

import sys
sys.path.append('../..')
from pyourfood import food
from pyourfood.population.population_data import UN_world_1950_2019, UN_world_2020_2100
from pyourfood.food.food_supply import FAOSTAT
from pyourfood.utils.calendar_tools import days_in_year

"""
FixOurFood intervention Dashboard

This graphical user interface is built using tkinter, which manages the actions
and positions of widgets, grouped into frames.
Each time an action is performed, the "plot" routine is called, which updates the information
going into generated the plots on the right.

There parent frame "window" has three child sub-frames which manage all the
important widgets of the dashboard:

- frame_categories

    Contains horizontal buttons which switch between the diferent types of interventions:
        - Dietary interventions
        - Farming interventions
        - Policy and Governance interventions

- frame_controls

    Contains all the controls, including buttons, sliders and labels, to interact with
    the different types of interventions.
    Depending on the selected category of interventions, different groups of widgets
    are packed and unpacked into frame_controls

- frame_plots

    This frame displays the relevant plots, as well as a dropdown menu to select which
    plot to show. On the bottom, there is a label explaining the basic concepts associated
    to the plots

"""

font = ("Courier", 12)

# load the food item data files for these codes
PN18 = pd.read_csv('PN18.csv', sep=':')
len_items = len(PN18)
len_groups = len(np.unique(PN18['group']))

index_label = np.unique(PN18['group'], return_index=True)[1]
group_names = [PN18['group'][index] for index in sorted(index_label)]

index_id = np.unique(PN18['group_id'], return_index=True)[1]
group_ids = [PN18['group_id'][index] for index in sorted(index_id)]

log_length = 25

FAOSTAT_years = np.unique(FAOSTAT.years)

FAOSTAT_years_all = np.concatenate([FAOSTAT_years, np.unique(UN_world_2020_2100.years)])

food_data = FAOSTAT.data

emissions = np.zeros((len_items, len(FAOSTAT_years_all)))
emissions_groups = np.zeros((len_groups, len(FAOSTAT_years_all)))
weight = np.zeros_like(emissions)
energy = np.zeros_like(emissions)
proteins = np.zeros_like(emissions)

# Last food supply estimated value is used as pivot value
# to scale as a function of projected population
past_population = UN_world_1950_2019.extract_year(FAOSTAT_years)
population_pivot = past_population.populations[-1]

population_ratio_projected = UN_world_2020_2100.populations / population_pivot

# First half of the array is filled with estimations from FAOSTAT food supply data
# Second half of the array is filled with scaled values according to population growth from pivot point
days = days_in_year(FAOSTAT_years)

for i, code in enumerate(PN18['code']):

    weight[i,:len(FAOSTAT_years)] = FAOSTAT.extract_item(code).food
    weight[i,len(FAOSTAT_years):] = weight[i,len(FAOSTAT_years)-1]

    emissions[i, :len(FAOSTAT_years)] = FAOSTAT.extract_item(code).food * days * PN18['mean_emissions'][i] * past_population.populations * 1e3 / 1e12
    emissions[i,len(FAOSTAT_years):] = population_ratio_projected * emissions[i,len(FAOSTAT_years)-1]

    energy[i,:len(FAOSTAT_years)] = FAOSTAT.extract_item(code).energy
    energy[i,len(FAOSTAT_years):] = energy[i,len(FAOSTAT_years)-1]

    proteins[i,:len(FAOSTAT_years)] = FAOSTAT.extract_item(code).protein
    proteins[i,len(FAOSTAT_years):] = proteins[i,len(FAOSTAT_years)-1]


glossary_dict = {
    "CO2 concentration":"""Atmospheric CO2 concentration
    measured in parts per million (PPM)""",

    "CO2 emission per food item":"""Fossil CO2 emissions to the atmosphere
    measured in billion tons per year""",

    "CO2 emission per food group":"""Fossil CO2 emissions to the atmosphere
    measured in billion tons per year""",

    "Radiative forcing":"""Balance between total energy
    absorved by Earth's atmosphere and total
    radiated energy back to space
    measured in Watts per square meter""",

    "Temperature anomaly":"""Difference in Celcius degrees
    between projected atmospheric temperature
    and baseline expected from stable emissions""",

    "Nutrients":""" Daily protein and energy intake per capita,
    in grams and kCal, respectively""",

    "Land Use":""" Distribution of land use accross the UK """,

    "Omnivorous diet":""" Omnivorous diets include the consumption of both
    plant and animal origin food items.""",

    "Semi-vegetarian diet":""" While not uniquely defined, semi-vegetarian diets
    normally include the consumption of animal origin products, typically meat,
    but limited to only certain species, or certain ocassions.""",

    "Pescetarian diet":""" Pescetarian diet limits the consumption of animal
    meat to only that coming from seafood and fish meat.""",

    "Lacto-ovo-vegetarian diet":""" Lacto-ovo-vegetarian diets limits the
    consumption of animal products to only dairy products and eggs,
    supressing any kind of meat consumption.""",

    "Vegan diet":""" Full vegetarian or vegan diets do not include any
    product of animal origin, thus eliminating the consumption of meat, dairy
    products and eggs.""",
}

vegetarian_diet_dict = {
    0:"""Omnivorous diet: Consumption of all types
    of food, including red (beef and goat) and white
    (pig, poultry) meat, fish and seafood, dairy
    products and eggs.""",

    1:"""Semi-vegetarian diet: Moderated consumption
    of meat, typically limited to white (pig, poultry)
    meat and seafood. Includes dairy products and
    eggs.""",

    2:"""Pescetarian diet: No red (beef, goat) or
    white (pig, poultry) meat consumption, processed
    animal protein only from fish and seafood.
    Includes dairy products and eggs.""",

    3:"""Vegetarian diet: No processed animal
    protein, including red (beef and goat), white
    (pig and poultry) meat or fish and seafood.
    Dairy products and eggs are consumed.""",

    4:"""Vegan diet: No products of animal origin
    are consumed. This includes red (beef and goat),
    white (pig and poultry) meat, fish and seafood
    or Dairy products and eggs"""
}

# Function to scale food item consumption to keep protein intake constant

# ruminant_slider   [0-4]
# veg_interv        [0,1]
# meatfree_slider   [0,7] if veg_interv == 1
# egg_checkbox      [0,1] if veg_interv == 1
# dairy_checkbox    [0,1] if veg_interv == 1
# vegetarian_slider [0,4] if veg_interv == 0

def timescale_factor(timescale, final_scale, length, start, model = 'linear'):
    base = np.ones(length)
    mu = 1 - final_scale
    if model == 'linear':
        gradient = np.arange(timescale) / timescale
        base[start : start + timescale] = 1 - mu*gradient
        base[start + timescale:] = final_scale
    elif model == 'logistic':
        gradient = 1 / (1 + np.exp(-0.5*(log_length + 1 - timescale)*(np.arange(log_length) - timescale / 2)))
        base[start : start + log_length] = 1 - mu*gradient
        base[start + log_length:] = final_scale
    return base

def scale_food(timescale, nutrient, ruminant, vegetarian_intervention, meatfree, vegetarian, seafood, eggs, dairy, model):

    # Scale down ruminant meat consumption.
    ruminant_fraction = (4-ruminant)/4
    adoption = 'logistic' if model else 'linear'

    ruminant_fraction = timescale_factor(timescale, ruminant_fraction, len(FAOSTAT_years_all), len(FAOSTAT_years)+1, model = adoption)
    meat_fraction = (7-meatfree)/7
    meat_fraction = timescale_factor(timescale, meat_fraction, len(FAOSTAT_years_all), len(FAOSTAT_years)+1, model = adoption)

    total_nutrient_group = [np.sum(nutrient[PN18['group_id'] == 0], axis=0) for i in range(12)]
    total_nutrient = np.sum(nutrient, axis=0)

    total_nutrient_meat = total_nutrient_group[0] + total_nutrient_group[1]
    total_nutrient_nomeat = total_nutrient - total_nutrient_meat
    total_nutrient_scaled_ruminant =  total_nutrient_group[0] * ruminant_fraction

    othermeat_fraction = meat_fraction * (total_nutrient_meat - total_nutrient_scaled_ruminant) / total_nutrient_group[1]

    # Meat Free Days
    if vegetarian_intervention == 0:
        total_nutrient_scaled_othermeat =  total_nutrient_group[1] * othermeat_fraction
        total_nutrient_scaled_meat = meat_fraction * (total_nutrient_scaled_othermeat + total_nutrient_scaled_ruminant)
        total_nutrient_minus_scaled_meat = total_nutrient - total_nutrient_scaled_meat

        for ac, ic in zip([eggs, dairy, seafood], [2, 3, 10]):
            total_nutrient_minus_scaled_meat += (1-meat_fraction) * ~ac * total_nutrient_group[ic]

        nomeat_fraction = total_nutrient_minus_scaled_meat / total_nutrient_nomeat
        food_scale = np.ones((len_items, len(FAOSTAT_years_all))) * nomeat_fraction

        ruminant_fraction *= meat_fraction
        total_nutrient_meat *= meat_fraction

        for ac, ic in zip([eggs, dairy, seafood], [2, 3, 10]):
            if not ac:
                food_scale[PN18['group_id'] == ic] *= meat_fraction

        food_scale[PN18['group_id'] == 0] = ruminant_fraction
        food_scale[PN18['group_id'] == 1] = othermeat_fraction

    # Type of vegetarian diet
    elif vegetarian_intervention == 1:
        one_minus_logistic = 1 - timescale_factor(timescale, 0, len(FAOSTAT_years_all), len(FAOSTAT_years)+1, model = adoption)
        if vegetarian == 0:
            total_nutrient_scaled_othermeat =  total_nutrient_group[1] * othermeat_fraction
            total_nutrient_scaled_meat = meat_fraction * (total_nutrient_scaled_othermeat + total_nutrient_scaled_ruminant)
            total_nutrient_minus_scaled_meat = total_nutrient - total_nutrient_scaled_meat
            nomeat_fraction = total_nutrient_minus_scaled_meat / total_nutrient_nomeat
            ruminant_fraction *= meat_fraction
            total_nutrient_meat *= meat_fraction
            food_scale = np.ones((len_items, len(FAOSTAT_years_all))) * nomeat_fraction

            food_scale[PN18['group_id'] == 0] = ruminant_fraction
            food_scale[PN18['group_id'] == 1] = othermeat_fraction

        else:
            total_vegetarian_nutrient = total_nutrient

            if vegetarian == 1: skip = [0]
            if vegetarian == 2: skip = [0, 1]
            if vegetarian == 3: skip = [0, 1, 10]
            if vegetarian == 4: skip = [0, 1, 10, 2, 3]

            for sk in skip:
                total_vegetarian_nutrient -= total_nutrient_group[sk] * one_minus_logistic

            vegetarian_fraction = total_nutrient / total_vegetarian_nutrient
            food_scale = np.ones((len_items, len(FAOSTAT_years_all)))*vegetarian_fraction

            for sk in skip:
                food_scale[PN18['group_id'] == sk] = 1 - one_minus_logistic

    food_scale[:, :len(FAOSTAT_years)] = 1
    return food_scale

# Functions to pack and unpack intervention widgets
def modify_option_menu(option_menu, menu_value, new_choices):

    menu_value.set('')
    option_menu['menu'].delete(0, 'end')

    for choice in new_choices:
        option_menu['menu'].add_command(label=choice, command=tk._setit(menu_value, choice, lambda _: plot()))
    plot_option.set(new_choices[0])

def pack_dietary_widgets():
    frame_farming.grid_forget()
    frame_policy.grid_forget()
    frame_diet.grid(row=0, column=0)
    button_diet.config(relief='sunken')
    button_farming.config(relief='raised')
    button_policy.config(relief='raised')

    new_choices = ("CO2 emission per food group",
        "CO2 emission per food item",
        "CO2 concentration",
        "Radiative forcing",
        "Temperature anomaly",
        "Nutrients")

    modify_option_menu(opt_plot, plot_option, new_choices)

def pack_farming_widgets():
    frame_policy.grid_forget()
    frame_diet.grid_forget()
    frame_farming.grid(row=0, column=0)
    button_diet.config(relief='raised')
    button_farming.config(relief='sunken')
    button_policy.config(relief='raised')

    new_choices = ("CO2 emission per food group",
        "CO2 emission per food item",
        "CO2 concentration",
        "Radiative forcing",
        "Temperature anomaly",
        "Land Use")

    modify_option_menu(opt_plot, plot_option, new_choices)


def pack_policy_widgets():
    frame_farming.grid_forget()
    frame_diet.grid_forget()
    frame_policy.grid(row=0, column=0)
    button_diet.config(relief='raised')
    button_farming.config(relief='raised')
    button_policy.config(relief='sunken')

    new_choices = ("CO2 emission per food group",
        "CO2 emission per food item",
        "CO2 concentration",
        "Radiative forcing",
        "Temperature anomaly")

    modify_option_menu(opt_plot, plot_option, new_choices)

def disable_meatfree():
    vegetarian_slider.configure(state='normal', fg='black')
    vegetarian_label.configure(fg='black')
    lbl_vegetarian_glossary.grid(row = 9, column = 0, columnspan=4, sticky='W')
    meatfree_slider.set(0)
    meatfree_slider.configure(state='disabled', fg='gray')
    meatfree_label.configure(fg='gray')
    seafood_checkbox.configure(state='disabled')
    egg_checkbox.configure(state='disabled')
    dairy_checkbox.configure(state='disabled')

def disable_vegetarian():
    meatfree_slider.configure(state='normal', fg='black')
    meatfree_label.configure(fg='black')
    seafood_checkbox.configure(state='normal')
    egg_checkbox.configure(state='normal')
    dairy_checkbox.configure(state='normal')
    vegetarian_slider.set(0)
    vegetarian_slider.configure(state='disabled', fg='gray')
    vegetarian_label.configure(fg='gray')
    lbl_vegetarian_glossary.grid_forget()

# function to generate the plots in tkinter canvas
def plot():

    # Read the selection and generate the arrays
    plot_key = plot_option.get()
    food_group_value = food_group_option.get()

    timescale = timescale_slider.get()
    ruminant = ruminant_slider.get()
    vegetarian_intervention = veg_interv.get()
    meatfree = meatfree_slider.get()
    seafood = seafood_choice.get()
    egg = egg_choice.get()
    dairy = dairy_choice.get()
    vegetarian = vegetarian_slider.get()
    year = year_choice.get()
    model = model_choice.get()

    if year:
        years = FAOSTAT_years_all
    else:
        years = FAOSTAT_years


    # Show or hide options to select food groups
    if plot_key == "CO2 emission per food item":
        food_group_menu.pack()
    else:
        food_group_menu.pack_forget()

    # Clear previous plots
    plot1.clear()
    plot2.clear()
    plot2.axis("off")

    # protein supply [g / capita / day] 674
    # kCal intake [kCal / capita / day] 664
    # consumed food weight [kg / capita / day] 10004

    if scaling_nutrient.get() == "Weight":
        nutrient = weight
    elif scaling_nutrient.get() == "Energy":
        nutrient = energy
    elif scaling_nutrient.get() == "Proteins":
        nutrient = proteins

    # obtain rescaled food supply
    food_scale = scale_food(timescale, nutrient, ruminant, vegetarian_intervention, meatfree, vegetarian, seafood, egg, dairy, model)

    scaled_emissions = emissions*food_scale
    scaled_energy = energy*food_scale
    scaled_proteins = proteins*food_scale

    # per capita food supply emissions [kg CO2e / capita / year]
    # This is computed multiplying the food supply per item (kg/capita/day)
    # by the global mean specific GHGE per item [kg CO2e / kg], by the country population
    # and by the number of days on a year

    # category_emissions = np.zeros((len_categories, len(FAOSTAT_years)))
    C, F, T = fair.forward.fair_scm(emissions=np.sum(scaled_emissions, axis = 0), useMultigas=False)

    plot1.axvline(2020, color = 'k', alpha = 0.5, linestyle = 'dashed')

    if plot_key == "CO2 concentration":
        plot1.plot(years, C[:len(years)], c = 'k')
        plot1.set_ylim((250,1700))
        plot1.set_ylabel(r"$CO_2$ concentrations (PPM)")

    elif plot_key == "CO2 emission per food group":

        for i, id in enumerate(group_ids):
            emissions_groups[i] = np.sum(scaled_emissions[PN18['group_id'] == id], axis=0)
        emissions_cumsum_group = np.cumsum(emissions_groups, axis=0)

        for i in reversed(range(len_groups)):
            plot1.fill_between(years, emissions_cumsum_group[i][:len(years)], label = group_names[i], alpha=0.5)
            plot1.plot(years, emissions_cumsum_group[i][:len(years)], color = 'k', linewidth=0.5)

        plot1.legend(loc=2, fontsize=7)
        plot1.set_ylim((-1,50))
        plot1.set_ylabel(r"Fossil $CO_2$ Emissions (GtC)")

    elif plot_key == "CO2 emission per food item":

        mask = PN18['group']==food_group_value
        emissions_cumsum = np.cumsum(scaled_emissions[mask], axis=0)
        food_names = PN18['name'][mask].values

        for i in reversed(range(len(food_names))):
            plot1.fill_between(years, emissions_cumsum[i][:len(years)], label = food_names[i], alpha=0.5)
            plot1.plot(years, emissions_cumsum[i][:len(years)], color='k', linewidth=0.5)

        plot1.legend(loc=2, fontsize=7)
        # plot1.set_ylim((-1,40))
        plot1.set_ylabel(r"Fossil $CO_2$ Emissions (GtC)")

    elif plot_key == "Nutrients":

        plot2.axis("on")
        plot1.plot(years, np.sum(scaled_energy, axis=0)[:len(years)], label = "Energy intake", color = 'Blue')
        # plot1.set_ylim((150,700))
        plot2.plot(years, np.sum(scaled_proteins, axis=0)[:len(years)], label = "Protein intake", color = 'Orange')
        # plot2.set_ylim((10,50))
        plot1.legend(loc=2, fontsize=7)
        plot2.legend(loc=1, fontsize=7)
        # plot1.set_ylim((-1,30))
        # plot1.set_ylabel(r"Fossil $CO_2$ Emissions (GtC)")

    elif plot_key == "Radiative forcing":
        plot1.plot(years, F[:len(years)], c = 'k')
        plot1.set_ylim((0,10))
        plot1.set_ylabel(r"Total Radiative Forcing $(W/m^2)$")

    elif plot_key == "Temperature anomaly":
        plot1.plot(years, T[:len(years)], c = 'k')
        plot1.set_ylim((0,5))
        plot1.set_ylabel(r"Temperature anomaly (K)")

    elif plot_key == "Land Use":
        plot1.plot(years, T[:len(years)], c = 'k')
        plot1.text(1975, 1, "placeholder plot for land use")
        plot1.set_ylim((0,5))
        plot1.set_ylabel(r"Temperature anomaly (K)")

    # elif plot_key == "Land use":



    plot1.set_xlabel("Year")
    canvas.draw()

    lbl_glossary.config(text=glossary_dict[plot_key], font=font)
    lbl_vegetarian_glossary.config(text=vegetarian_diet_dict[vegetarian_slider.get()], font=font)


# -----------------------------------------
#       MAIN WINDOW
# -----------------------------------------

window = tk.Tk()
window.geometry('960x980')
window.title('FixOurFood FAIR carbon emission model')

frame_categories = tk.Frame(window)
frame_controls = tk.Frame(window)
frame_plots = tk.Frame(window)

frame_categories.pack(side = tk.TOP)
frame_controls.pack(side=tk.LEFT)
frame_plots.pack(side=tk.RIGHT)

# -----------------------------------------
#       INTERVENTION CATEGORIES
# -----------------------------------------

button_diet = tk.Button(frame_categories, text = "Dietary interventions", command=pack_dietary_widgets, font=font)
button_farming = tk.Button(frame_categories, text = "Farming interventions", command=pack_farming_widgets, font=font)
button_policy = tk.Button(frame_categories, text = "Policy and Governance interventions", command=pack_policy_widgets, font=font)

button_diet_ttp = CreateToolTip(button_diet, \
'Interventions to diet and alimentary practices. '
'Typically involve a modification on consumed food items '
'and individual-level food consuming practices.')

button_farming_ttp = CreateToolTip(button_farming, \
'Interventions to farming practices. '
'Mainly focused on food production, storage and distributions, '
'and waste management.')

button_policy_ttp = CreateToolTip(button_policy, \
'Interventions to policy and governance regulations. '
'Evaluate the effect of regulations and legislation practices '
'on food environmental impact')

button_diet.pack(side = tk.LEFT)
button_farming.pack(side = tk.LEFT)
button_policy.pack(side = tk.LEFT)

# -----------------------------------------
#         INTERVENTION CONTROLS
# -----------------------------------------

# ** Dietary intervention widgets **

# The widgets below control the following variables which are then used to scale
# food supply values according to the modellinf for each intervention

# ruminant_slider   [0-4]
# veg_interv        [0,1]
# meatfree_slider   [0,7] if veg_interv == 1
# egg_checkbox      [0,1] if veg_interv == 1
# dairy_checkbox    [0,1] if veg_interv == 1
# vegetarian_slider [0,4] if veg_interv == 0
# scaling_nutrient  ['Weight', 'Proteins', 'Energy']

frame_diet = tk.Frame(frame_controls)

scaling_nutrient = tk.StringVar(value='Weight')
tk.Label(frame_diet, text = "Replace by", font=font).grid(row = 0, column = 0, sticky='W')
for ic, label in enumerate(['Weight', 'Proteins', 'Energy']):
    tk.Radiobutton(frame_diet, text = label,   variable = scaling_nutrient, value = label,   command=plot, font=font).grid(row = 0, column = ic+1, sticky='W')

ruminant_label = tk.Label(frame_diet, text="Reduce ruminant meat consumption", font=font)
ruminant_slider = tk.Scale(frame_diet, from_=0, to=4, orient=tk.HORIZONTAL, command= lambda _: plot())
CreateToolTip(ruminant_slider, \
'0: 0% ruminant meat reduction \n'
'1: 25% ruminant meat reduction \n'
'2: 50% ruminant meat reduction \n'
'3: 75% ruminant meat reduction \n'
'4: 100% ruminant meat reduction')

veg_interv = tk.IntVar(0)
# Meat-free days
meatfree_rdbtn = tk.Radiobutton(frame_diet, text = 'Meat free days', variable = veg_interv, value = 0, command=disable_vegetarian, font=font)
CreateToolTip(meatfree_rdbtn, \
'Meat to be consumed on meat-free days '
'is replaced by an increase consumption '
'of selected items to supply replacement nutrients.')
meatfree_label = tk.Label(frame_diet, text="Number of meat-free days", font=font)
meatfree_slider = tk.Scale(frame_diet, from_=0, to=7, orient=tk.HORIZONTAL, command= lambda _: plot())
CreateToolTip(meatfree_slider, \
'Choose the number of days a week '
'with no meat consumption')

# Fish & seafood, egg and dairy products selector
seafood_choice = tk.BooleanVar()
seafood_choice.set(True)
egg_choice = tk.BooleanVar()
egg_choice.set(True)
dairy_choice = tk.BooleanVar()
dairy_choice.set(True)

seafood_checkbox = tk.Checkbutton(frame_diet, text = 'Fish & Seafood', offvalue = False, onvalue = True, variable = seafood_choice, command = plot)
CreateToolTip(seafood_checkbox,
'Include Fish and seafood in the meat-free day diets?')

egg_checkbox = tk.Checkbutton(frame_diet, text = 'Eggs', offvalue = False, onvalue = True, variable = egg_choice, command = plot)
CreateToolTip(egg_checkbox,
'Include eggs in the meat-free day diets?')

dairy_checkbox = tk.Checkbutton(frame_diet, text = 'Dairy products', offvalue = False, onvalue = True, variable = dairy_choice, command = plot)
CreateToolTip(dairy_checkbox,
'Include dairy products in the meat-free day diets?')

# Vegetarian diets
vegetarian_rdbtn = tk.Radiobutton(frame_diet, text = 'Type of vegetarian diet', variable = veg_interv, value = 1, command=disable_meatfree, font=font)
CreateToolTip(vegetarian_rdbtn, \
'Meat consumption is replaced by '
'an increase consumption of selected items '
'to supply replacement nutrients.')
vegetarian_label = tk.Label(frame_diet, text="Vegetarian diet", font=font, fg='gray')
vegetarian_slider = tk.Scale(frame_diet, from_=0, to=4, orient=tk.HORIZONTAL, command= lambda _: plot(), state='disabled', fg='gray')
CreateToolTip(vegetarian_slider, \
'0: Omnivorous diet \n'
'1: Semi-vegetarian diet \n'
'2: Pescetarian diet \n'
'3: Vegetarian diet \n'
'4: Vegan diet')

# Widget packing using grid
ruminant_label.grid(row = 1, column = 0, columnspan=2)
ruminant_slider.grid(row = 1, column = 2)

meatfree_rdbtn.grid(row = 2, column = 0, sticky='W')
meatfree_label.grid(row = 3, column = 0, columnspan=2)
meatfree_slider.grid(row = 3, column = 2)
seafood_checkbox.grid(row = 4, column = 2, sticky='W')
egg_checkbox.grid(row = 5, column = 2, sticky='W')
dairy_checkbox.grid(row = 6, column = 2, sticky='W')

vegetarian_rdbtn.grid(row = 7, column = 0, sticky='W')
vegetarian_label.grid(row = 8, column = 0, columnspan=2)
vegetarian_slider.grid(row = 8, column = 2)

# Glossary widget
lbl_vegetarian_glossary = tk.Label(frame_diet, text = vegetarian_diet_dict[vegetarian_slider.get()])
# lbl_vegetarian_glossary.grid(row = 8, column = 0, columnspan=2, sticky='W')

# ** Farming intervention widgets **

frame_farming = tk.Frame(frame_controls)

for irow in range(5):
    tk.Scale(frame_farming, from_=0, to=4, orient=tk.HORIZONTAL, command= lambda _: plot()).grid(row = irow, column = 3)

tk.Label(frame_farming, text="Improve manure treatment",       font=font).grid(row = 0, column  = 0, columnspan=3)
tk.Label(frame_farming, text="Improve breeding",               font=font).grid(row = 1, column  = 0, columnspan=3)
tk.Label(frame_farming, text="Improve stock feed composition", font=font).grid(row = 2, column  = 0, columnspan=3)
tk.Label(frame_farming, text="Grazing versus feedlot",         font=font).grid(row = 3, column  = 0, columnspan=3)
tk.Label(frame_farming, text="Use calves from dairy herd",     font=font).grid(row = 4, column  = 0, columnspan=3)

# ** Policy intervention widgets **

frame_policy = tk.Frame(frame_controls)


# -----------------------------------------
#           PLOT CANVAS
# -----------------------------------------

# Plot option dropdown menu
option_list = ["CO2 emission per food group", "CO2 emission per food item", "CO2 concentration", "Radiative forcing", "Temperature anomaly", "Nutrients"]
plot_option = tk.StringVar(value="CO2 emission per food group")
opt_plot = tk.OptionMenu(frame_plots, plot_option, *option_list, command = lambda _: plot())
opt_plot.config(font=font)
opt_plot.pack()

# Year range option
year_choice = tk.BooleanVar()
year_choice.set(True)
year_checkbox = tk.Checkbutton(frame_plots, text = 'Include future projections', offvalue = False, onvalue = True, variable = year_choice, command = plot)
CreateToolTip(year_checkbox,
'Include population growth projections '
'by the UN for the 2020-2100 period.')
year_checkbox.pack()

model_choice = tk.BooleanVar()
model_choice.set(True)
model_checkbox = tk.Checkbutton(frame_plots, text = 'Adoption model', offvalue = False, onvalue = True, variable = model_choice, command = plot)
CreateToolTip(model_checkbox,
'Use a logistic model instead of a linear model for interention adoption timescale')
model_checkbox.pack()

timescale_slider = tk.Scale(frame_plots, from_=1, to=log_length, orient=tk.HORIZONTAL, command= lambda _: plot())
CreateToolTip(timescale_slider, \
'Select the timescale in years over which the transformation '
'takes place. 0 means the transformation occurs immediately.')
timescale_slider.pack()

# Figure widget
fig, plot1 = plt.subplots(figsize = (5,5))
plot2 = plot1.twinx()

fig.patch.set_facecolor('#D9D9D9')

canvas = FigureCanvasTkAgg(fig, frame_plots)
canvas.get_tk_widget().pack()


# Glossary widget
lbl_glossary = tk.Label(frame_plots, text = glossary_dict[plot_option.get()])
lbl_glossary.pack()

# Fodd group dropdown menu
food_group_option = tk.StringVar(value = group_names[0])
food_group_menu = tk.OptionMenu(frame_plots, food_group_option, *group_names, command = lambda _: plot())
food_group_menu.config(font=font)
food_group_menu.pack()

################# Setup #################

pack_dietary_widgets()
plot()

################ Loop ###################
window.mainloop()
