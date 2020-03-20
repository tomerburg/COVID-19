#Import packages & other scripts
import pickle
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import read_data
from color_gradient import Gradient

#========================================================================================================
# User-defined settings
#========================================================================================================

#Report date(s) to plot
plot_start_date = dt.datetime(2020,2,20)
plot_end_date = dt.datetime(2020,3,19)
plot_end_today = True #If true, overrides plot_end_date

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, deaths, recovered, active, daily)
plot_type = "deaths"

#Include repatriated cases (e.g., cruises)?
include_repatriated = True

#Plot total numbers?
plot_total = True

#Whether to use data from Worldometers from March 18th onwards
worldometers = True

#Read from local file? (WARNING = ensure data sources are the same!)
read_from_local = False

#========================================================================================================
# Get COVID-19 case data
#========================================================================================================

repatriated_locations = ['diamond princess',
                         'grand princess']

"""
COVID-19 case data is retrieved from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19
"""

#Avoid re-reading case data if it's already stored in memory
try:
    cases
except:
    print("--> Reading in COVID-19 case data from Johns Hopkins CSSE")

    if worldometers == True: include_repatriated = False
    if read_from_local == True:
        cases = pickle.load(open('cases_us.pickle','rb'))
        dates = cases['dates']
        del cases['dates']
    else:
        output = read_data.read_us(negative_daily=False,worldometers=worldometers)
        dates = output['dates']
        cases = output['cases']
    
    if plot_end_today == True: plot_end_date = dates[-1]

#========================================================================================================
# Create plot based on type
#========================================================================================================

#Function for returning number within range
def return_val(start_range,end_range,start_size,end_size,val):
    frac = (val-start_range)/(end_range-start_range)
    frac = (frac * (end_size-start_size)) + start_size
    return frac

#Total count
total_count = np.array([0.0 for i in cases['new york']['date']])
total_count_row = np.array([0.0 for i in cases['new york']['date']])

#Empty array
data_annot = []
data = []
rows = []

#Iterate through every region
sorted_keys = [y[1] for y in sorted([(cases[x][plot_type][-1], x) for x in cases.keys()])][::-1]
sorted_value = [y[0] for y in sorted([(cases[x][plot_type][-1], x) for x in cases.keys()])][::-1]
for idx,(key,value) in enumerate(zip(sorted_keys,sorted_value)):

    #Special handling for Diamond Princess
    if include_repatriated == False and key in repatriated_locations: continue

    #Total count
    total_count += np.array(cases[key][plot_type])
    if key not in repatriated_locations: total_count_row += np.array(cases[key][plot_type])

    #Get start and end indices
    idx_start = dates.index(plot_start_date)
    idx_end = dates.index(plot_end_date)

    #Append to data
    data_annot.append(['-' if i == 0 or np.isnan(i) == True else str(i) for i in cases[key][plot_type][idx_start:idx_end+1]])
    data.append(cases[key][plot_type][idx_start:idx_end+1])

    #Append location to row
    name = key.upper() if key in ['uk','us'] else key.title()
    rows.append(name)

#Add column and row labels
columns = [i.strftime('%b\n%d') for i in dates][idx_start:idx_end+1]

#Add total?
if plot_total == True:
    data_annot.insert(0,['-' if i == 0 or np.isnan(i) == True else str(int(i)) for i in total_count][idx_start:idx_end+1])
    data.insert(0,[0 if np.isnan(i) == True else int(i) for i in total_count][idx_start:idx_end+1])
    rows.insert(0,"U.S. Total")

#Create data colormap
max_val = 0.0
for line in data:
    max_val = line[-1] if line[-1] > max_val else max_val
if max_val < 40: max_val = 40

color_obj = Gradient([['#EEEEEE',0.0],['#EEEEEE',0.9]],
                     [['#FFFF00',0.9],['#EE7B51',int(max_val*0.08)]],
                     [['#EE7B51',int(max_val*0.08)],['#B53079',int(max_val*0.3)]],
                     [['#B53079',int(max_val*0.3)],['#070092',int(max_val*0.7)]],
                     [['#070092',int(max_val*0.7)],['#000000',int(max_val*1.2)]])

#Retrieve colormap
clevs = np.append(np.array([0,0.95,1.0]),np.arange(2,max_val,1))
cmap = color_obj.get_cmap(clevs)

#Determine figure width
mval = np.nanmax(data)
if mval > 100000:
    fig_width = return_val(start_range=27, end_range=92, start_size=29, end_size=98, val=len(columns))
elif mval > 10000:
    fig_width = return_val(start_range=27, end_range=92, start_size=24, end_size=80, val=len(columns))
elif mval > 1000:
    fig_width = return_val(start_range=21, end_range=40, start_size=17.5, end_size=30, val=len(columns))
else:
    fig_width = return_val(start_range=27, end_range=92, start_size=12, end_size=41, val=len(columns))
if fig_width < 14: fig_width = 14

#Create figure
fig,ax = plt.subplots(figsize=(fig_width,16),dpi=150) #32,2

#Reformat data into Pandas DataFrame
data_df = pd.DataFrame(data,index=rows,columns=columns)

#Plot seaborn heatmap
ax = sns.heatmap(data_df, xticklabels=True, yticklabels=True, cmap=cmap, linewidths=0.5,
                 cbar_kws = dict(use_gridspec=False,location="bottom",fraction=0.05, pad=0.008),
                 annot_kws = dict(fontsize=12), annot=np.array(data_annot), fmt = '')

#Format ticks
ax.tick_params(right=True, top=True, labelright=True, labeltop=True,
               bottom=False, labelbottom=False)
ax.set_yticklabels(labels=rows, rotation=360)

#Separate line for plotting total
if plot_total == True:
    ax.hlines([1], *ax.get_xlim())

#Plot title
title_string = {
    'confirmed':'Cumulative COVID-19 Confirmed Cases',
    'deaths':'Cumulative COVID-19 Deaths',
    'recovered':'Cumulative COVID-19 Recovered Cases',
    'active':'Daily COVID-19 Active Cases',
    'daily':'Daily COVID-19 New Cases',
}
add_title = "(Non-Repatriated)" if include_repatriated == False else ""
plt.title(f"{title_string.get(plot_type)} {add_title}",fontweight='bold',loc='left',fontsize=14, pad=50)

#Add data source
if worldometers == True:
    plt.title(f"Data from Johns Hopkins CSSE\nWorldometers From 18 March onward",loc='right',fontsize=10, pad=50, color='blue')
else:
    plt.title(f"Data from Johns Hopkins CSSE",loc='right',fontsize=10, pad=50, color='blue')

#Show plot and close
if save_image['setting'] == True:
    savepath = os.path.join(save_image['directory_path'],f"{plot_type}_us_table.png")
    plt.savefig(savepath,bbox_inches='tight')
else:
    plt.show()
plt.close()

#Alert script is done
print("Done!")
