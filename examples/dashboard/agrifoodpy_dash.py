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
from agrifoodpy.food.food_supply import FAOSTAT, Nutrients_FAOSTAT, scale_food, plot_years, plot_bars
from agrifoodpy.impact.impact import PN18_FAOSTAT
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

window = tk.Tk()
font = tk.font.Font(family="times", size=12, weight="bold")

# ----------------------
# Regional configuration
# ----------------------

area_pop = 826 #UK
area_fao = 229 #UK
years = np.arange(1961, 2101)

# ------------------------------
# Select population data from UN
# ------------------------------

pop_uk = UN.Medium.sel(Region=area_pop, Year=years)*1000

pop_past = pop_uk[pop_uk["Year"] < 2020]
pop_future = pop_uk[pop_uk["Year"] >= 2020]
proj_pop_ones = xr.ones_like(pop_future)

# ---------------------------
# Match FAOSTAT and PN18 data
# ---------------------------
co2e_g = PN18_FAOSTAT["GHG Emissions"]/1000

# -----------------------------------------
# Define food item
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

# -----------------------------------------
# Select food consumption data from FAOSTAT
# -----------------------------------------

# 1000Ton_food / Year
food_uk = FAOSTAT.sel(Region=area_fao, Item=items_uk).drop(["domestic", "residual", "tourist"])

meat_items = food_uk.sel(Item=food_uk.Item_group=="Meat").Item.values
animal_items = food_uk.sel(Item=food_uk.Item_origin=="Animal Products").Item.values
plant_items = food_uk.sel(Item=food_uk.Item_origin=="Vegetal Products").Item.values

# g_food / cap / day
food_cap_day_baseline = food_uk*1e9/pop_past/365.25
food_cap_day_baseline = xr.concat([food_cap_day_baseline, food_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")

# kCal, g_pot, g_fat / g_food
kcal_g = Nutrients_FAOSTAT.kcal.sel(Region=229)
prot_g = Nutrients_FAOSTAT.protein.sel(Region=229)
fats_g = Nutrients_FAOSTAT.fat.sel(Region=229)

# kCal, g_pot, g_fat, g_co2e / cap / day
kcal_cap_day_baseline = food_cap_day_baseline * kcal_g
prot_cap_day_baseline = food_cap_day_baseline * prot_g
fats_cap_day_baseline = food_cap_day_baseline * fats_g
co2e_cap_day_baseline = food_cap_day_baseline * co2e_g

kcal_cap_day_baseline = xr.concat([kcal_cap_day_baseline, kcal_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")
prot_cap_day_baseline = xr.concat([prot_cap_day_baseline, prot_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")
fats_cap_day_baseline = xr.concat([fats_cap_day_baseline, fats_cap_day_baseline.sel(Year=2019) * proj_pop_ones], dim="Year")

# g_food, kCal, g_pot, g_fat, g_co2e / Year
food_year_baseline = food_cap_day_baseline * pop_uk * 365.25
kcal_year_baseline = kcal_cap_day_baseline * pop_uk * 365.25
prot_year_baseline = prot_cap_day_baseline * pop_uk * 365.25
fats_year_baseline = fats_cap_day_baseline * pop_uk * 365.25
co2e_year_baseline = co2e_cap_day_baseline * pop_uk * 365.25

baseline = {"Weight":food_year_baseline,
            "Energy":kcal_year_baseline,
            "Fat":fats_year_baseline,
            "Proteins":prot_year_baseline,
            "Emissions":co2e_year_baseline}

# --------------------------------
# String and glossary dictionaries
# --------------------------------
group_names = np.unique(food_uk.Item_group.values)

from glossary import option_list, glossary_dict, vegetarian_diet_dict


def logistic(k, x0, xmax, xmin=0):
    return 1 / (1 + np.exp(-k*(np.arange(xmax-xmin) - x0)))

# Functions to pack and unpack intervention widgets
def modify_option_menu(option_menu, menu_value, new_choices):
    menu_value.set('')
    option_menu['menu'].delete(0, 'end')

    for choice in new_choices:
        option_menu['menu'].add_command(label=choice, command=tk._setit(menu_value, choice, lambda _: plot()))
    menu_value.set(new_choices[0])

def pack_dietary_widgets():
    frame_farming.grid_forget()
    frame_policy.grid_forget()
    frame_diet.grid(row=0, column=0)
    button_diet.config(relief='sunken')
    button_farming.config(relief='raised')
    button_policy.config(relief='raised')

    modify_option_menu(opt_plot, plot_option, option_list)

def pack_farming_widgets():
    frame_policy.grid_forget()
    frame_diet.grid_forget()
    frame_farming.grid(row=0, column=0)
    button_diet.config(relief='raised')
    button_farming.config(relief='sunken')
    button_policy.config(relief='raised')

    modify_option_menu(opt_plot, plot_option, option_list)

def pack_policy_widgets():
    frame_farming.grid_forget()
    frame_diet.grid_forget()
    frame_policy.grid(row=0, column=0)
    button_diet.config(relief='raised')
    button_farming.config(relief='raised')
    button_policy.config(relief='sunken')

    modify_option_menu(opt_plot, plot_option, option_list)

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

    # ----------------
    # Get plot options
    # ----------------

    plot_key = plot_option.get() # which plot is being shown
    option_key = plot_suboption.get() # additional option for the plot

    k = timescale_slider.get() / 10 # [1,10]

    ruminant = ruminant_slider.get() # [0,4]
    meatfree = meatfree_slider.get() # [0,7] if veg_interv == 1

    seafood = seafood_choice.get() # [0,1] if veg_interv == 1
    egg = egg_choice.get() # [0,1] if veg_interv == 1
    dairy = dairy_choice.get() # [0,1] if veg_interv == 1

    nutrient = baseline[scaling_nutrient.get()]

    x0 = 70
    scale_ruminant = xr.DataArray(data = 1-(ruminant/4)*logistic(k, x0, 2101-1961), coords = {"Year":years})

    aux = scale_food(food=nutrient,
                         scale= scale_ruminant,
                         origin="imports",
                         items=groups["RuminantMeat"],
                         constant=True,
                         fallback="exports")

    scale_meatfree = xr.DataArray(data = 1-(meatfree/7)*logistic(k, x0, 2101-1961), coords = {"Year":years})

    extra_items = np.concatenate((groups["RuminantMeat"], groups["OtherMeat"]))
    if seafood:
        extra_items = np.concatenate((extra_items, groups["FishSeafood"]))
    if egg:
        extra_items = np.concatenate((extra_items, groups["Egg"]))
    if dairy:
        extra_items = np.concatenate((extra_items, groups["Dairy"]))

    aux = scale_food(food=aux,
                         scale= scale_meatfree,
                         origin="imports",
                         items=extra_items,
                         constant=True,
                         fallback="exports")

    scaling = aux / nutrient
    co2e_year = co2e_year_baseline * scaling

    # Clear previous plots
    plot1.clear()
    plot2.clear()
    plot2.axis("off")

    # Plot
    if plot_key == "CO2e concentration":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, C, c = 'k')
        plot1.set_ylabel(r"$CO_2$ concentrations (PPM)")

    elif plot_key == "CO2e emission per food group":

        # For some reason, xarray does not preserves the coordinates dtypes.
        # Here, we manually assign them to strings again to allow grouping by Non-dimension coordinate strigns
        co2e_year.Item_group.values = np.array(co2e_year.Item_group.values, dtype=str)
        co2e_year_groups = co2e_year.groupby("Item_group").sum().rename({"Item_group":"Item"})
        plot_years(co2e_year_groups["food"], ax=plot1)
        plot1.set_ylim(0, 4e11)

    elif plot_key == "Nutrients":
        pass

    elif plot_key == "Radiative forcing":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, F, c = 'k')
        plot1.set_ylabel(r"Total Radiative Forcing $(W/m^2)$")

    elif plot_key == "Temperature anomaly":

        # Compute emissions using FAIR
        total_emissions_gtco2e = (co2e_year["food"]*scaling["food"]).sum(dim="Item").to_numpy()/1e12
        C, F, T = fair.forward.fair_scm(total_emissions_gtco2e, useMultigas=False)
        plot1.plot(co2e_year.Year.values, T, c = 'k')
        plot1.set_ylabel(r"Temperature anomaly (K)")

    elif plot_key == "Land Use":
        pass

    elif plot_key == "CO2e emission per food item":

        if option_key not in group_names:
            modify_option_menu(suboption_menu, plot_suboption, group_names)
            option_key = plot_suboption.get()

        # Can't index by alternative coordinate name, use xr.where instead and squeeze
        co2e_year_item = co2e_year.sel(Item=co2e_year["Item_group"] == option_key).squeeze()
        plot_years(co2e_year_item["food"], ax=plot1)
        plot1.set_ylim(bottom=0)

    elif plot_key == "FAOSTAT Elements":

        if option_key not in baseline.keys():
            modify_option_menu(suboption_menu, plot_suboption, list(baseline.keys()))
            option_key = plot_suboption.get()

        bar_plot_baseline = baseline[option_key]

        bar_plot_array = bar_plot_baseline * scaling
        bar_plot_array.Item_origin.values = np.array(bar_plot_array.Item_origin.values, dtype=str)
        bar_plot_array_groups = bar_plot_array.groupby("Item_origin").sum().rename({"Item_origin":"Item"})

        plot_bars(bar_plot_array_groups.sel(Year=2099), labels=bar_plot_array_groups.Item.values, ax=plot1)
        # plot1.set_xlim(0,x_limit)

    lbl_glossary.config(text=glossary_dict[plot_key], font=font)
    lbl_vegetarian_glossary.config(text=vegetarian_diet_dict[vegetarian_slider.get()], font=font)

    canvas.draw()

# -----------------------------------------
#       MAIN WINDOW
# -----------------------------------------

window.geometry('960x980')
window.title('FixOurFood FAIR carbon emission model')

frame_categories = tk.Frame(window)
frame_controls = tk.Frame(window)
frame_plots = tk.Frame(window)

font = tk.font.Font(family="Helvetica", size=12)

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
for ic, label in enumerate(['Weight', 'Proteins', 'Fat', 'Energy']):
    tk.Radiobutton(frame_diet, text=label, variable=scaling_nutrient, value=label, command=plot, font=font).grid(row = ic, column = 1, sticky='W')

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
ruminant_label.grid(row = 4, column = 0, columnspan=2)
ruminant_slider.grid(row = 4, column = 2)

meatfree_rdbtn.grid(row = 5, column = 0, sticky='W')
meatfree_label.grid(row = 6, column = 0, columnspan=2)
meatfree_slider.grid(row = 7, column = 2)
seafood_checkbox.grid(row = 8, column = 2, sticky='W')
egg_checkbox.grid(row = 8, column = 2, sticky='W')
dairy_checkbox.grid(row = 9, column = 2, sticky='W')

vegetarian_rdbtn.grid(row = 10, column = 0, sticky='W')
vegetarian_label.grid(row = 11, column = 0, columnspan=2)
vegetarian_slider.grid(row = 11, column = 2)

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

plot_option = tk.StringVar(value="FAOSTAT Elements")
opt_plot = tk.OptionMenu(frame_plots, plot_option, *option_list, command = lambda _: plot())
opt_plot.config(font=font)
opt_plot.pack()

# Year range option
year_choice = tk.BooleanVar()
year_choice.set(True)
year_checkbox = tk.Checkbutton(frame_plots, text = 'Include future projections', offvalue = False, onvalue = True, variable = year_choice, command = plot, font=font)
CreateToolTip(year_checkbox,
'Include population growth projections '
'by the UN for the 2020-2100 period.')
year_checkbox.pack()

model_choice = tk.BooleanVar()
model_choice.set(True)
model_checkbox = tk.Checkbutton(frame_plots, text = 'Adoption model', offvalue = False, onvalue = True, variable = model_choice, command = plot, font=font)
CreateToolTip(model_checkbox,
'Use a logistic model instead of a linear model for interention adoption timescale')
model_checkbox.pack()

timescale_slider = tk.Scale(frame_plots, from_=1, to=10, orient=tk.HORIZONTAL, command= lambda _: plot())
CreateToolTip(timescale_slider, \
'Select the timescale in years over which the transformation '
'takes place. 0 means the transformation occurs immediately.')
timescale_slider.pack()

# Figure widget
fig, plot1 = plt.subplots(figsize = (8,6))
plot2 = plot1.twinx()
# plt.tight_layout()

fig.patch.set_facecolor('#D9D9D9')

canvas = FigureCanvasTkAgg(fig, frame_plots)
canvas.get_tk_widget().pack()

# Glossary widget
lbl_glossary = tk.Label(frame_plots, text = glossary_dict[plot_option.get()])
lbl_glossary.pack()

# Plot option dropdown menu
plot_suboption = tk.StringVar(value = group_names[0])
suboption_menu = tk.OptionMenu(frame_plots, plot_suboption, *group_names, command = lambda _: plot())
suboption_menu.config(font=font)
suboption_menu.pack()

################# Setup #################

pack_dietary_widgets()
plot()

################ Loop ###################
window.mainloop()
