import tkinter as tk
from CreateToolTip import *

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import fair
from fair.RCPs import rcp3pd, rcp45, rcp6, rcp85

from agrifoodpy import food
from agrifoodpy.population.population_data import UN
from agrifoodpy.food.food_supply import FAOSTAT, scale_food
from agrifoodpy.impact.impact import PN18
from agrifoodpy.impact import impact

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


# ----------------------
# GUI configuration
# ----------------------

font = ("Courier", 12)
log_length = 25


# ----------------------
# Regional configuration
# ----------------------

area_pop = 826 #UK
area_fao = 229 #UK
years = np.arange(1961, 2100)

# ------------------------------
# Select population data from UN
# ------------------------------

pop_uk = UN.Medium.sel(Region=area_pop, Year=years)*1000

pop_past = pop_uk[pop_uk["Year"] < 2020]
pop_pivot = pop_uk[pop_uk["Year"] == 2020]
pop_future = pop_uk[pop_uk["Year"] >= 2020]
proj_pop_ratio = pop_future / pop_pivot.values

# ---------------------------
# Match FAOSTAT and PN18 data
# ---------------------------
matching = pd.read_csv("PN18 and FAOSTAT list matching matrix.csv", sep=":")

alternative = matching["Alternative"]
alt_mask = ~np.isnan(alternative)

matching.drop("Alternative", axis=1, inplace=True)
matching.fillna(0, inplace=True)

food_impact = impact.match(PN18, matching)
food_impact["GHG Emissions"].values[alt_mask] = alternative[alt_mask]

co2e_g = food_impact["GHG Emissions"]/1000

# -----------------------------------------
# Define food item groups
# -----------------------------------------

groups = {
    "Cereals" : np.array([2511, 2513, 2514, 2515, 2516, 2517, 2518, 2520, 2531, 2532, 2533, 2534, 2535, 2807]),
    "Pulses" : np.array([2546, 2547, 2549, 2555]),
    "Sugar" : np.array([2536, 2537, 2541, 2542, 2543, 2558, 2562, 2570, 2571, 2572, 2573, 2574, 2576, 2577, 2578, 2579, 2580, 2581, 2582, 2586, 2745]),
    "NutsSeed" : np.array([2551, 2552, 2557, 2560, 2561]),
    "VegetablesFruits" : np.array([2563, 2601, 2602, 2605, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2625, 2641, 2775]),
    "RuminantMeat" : np.array([2731, 2732]),
    "OtherMeat" : np.array([2733, 2734, 2735, 2736]),
    "Egg" : np.array([2949]),
    "Dairy" : np.array([2740, 2743, 2948]),
    "FishSeafood" : np.array([2761, 2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769]),
    "Other" : np.array([2630, 2633, 2635, 2640, 2642, 2645, 2655, 2656, 2657, 2658, 2680, 2737]),
    "NonFood" : np.array([2559, 2575, 2659, 2781, 2782])
}

items_uk = np.hstack(list(groups.values()))

group_labels = []
group_names = list(groups.keys())

for item in items_uk:
    for ig, group in enumerate(group_names):
        if item in groups[group]:
            group_labels.append(list(groups.keys())[ig])


# -----------------------------------------
# Select food consumption data from FAOSTAT
# -----------------------------------------

elements_dict = {'production':0,
            'imports':1,
            'exports':2,
            'stock':3,
            'feed':4,
            'seed':5,
            'losses':6,
            'processing':7,
            'other':8,
            'food':9,}

food_uk = FAOSTAT.sel(Region=area_fao, Item=items_uk)
food_uk = food_uk.assign_coords(dict(group=("Item", group_labels)))

kcal_day = food_uk["kcal"]
prot_day = food_uk["protein"]
fats_day = food_uk["fat"]

food_uk = food_uk[list(elements_dict.keys())]*1e9/pop_past/365.25
food_uk = xr.concat([food_uk, food_uk.sel(Year=2019) * proj_pop_ratio], dim="Year")

kcal_g = kcal_day / food_uk["food"]
prot_g = prot_day / food_uk["food"]
fats_g = fats_day / food_uk["food"]

kcal_day_food_uk = food_uk * kcal_g
prot_day_food_uk = food_uk * prot_g
fats_day_food_uk = food_uk * fats_g
co2e_day_food_uk = food_uk * co2e_g

kcal_food_uk = kcal_day_food_uk * pop_uk
prot_food_uk = prot_day_food_uk * pop_uk
fats_food_uk = fats_day_food_uk * pop_uk
co2e_food_uk = co2e_day_food_uk * pop_uk

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


# timescale : int from 1 to log_length
# nutrient : string one of "weight, Energy, Proteins"
# ruminant : int from 0 to 4
# vegetarian_intervention : boolean
# meatfree : int from 0 to 7
# vegetarian : boolean
# seafood : boolean
# eggs : boolean
# dairy : boolean
# model : boolean

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

def plot():

    to_plot = co2e_food_uk

    to_plot_groups = to_plot.groupby("group").sum()

    to_plot_groups_cumsum = to_plot_groups["food"].cumsum(dim="group")
    years = to_plot_groups_cumsum.Year.values
    for ig in reversed(range(len(groups))):
        plot1.fill_between(years, to_plot_groups_cumsum[ig], alpha=0.5)
        plot1.plot(years, to_plot_groups_cumsum[ig], color='k', linewidth=0.5)

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
