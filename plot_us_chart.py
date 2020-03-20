#Import packages & other scripts
import pickle
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import read_data

#========================================================================================================
# User-defined settings
#========================================================================================================

#Start week of plot
start_week = 3

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, confirmed_normalized, deaths, recovered, active, daily)
plot_type = "confirmed"

#Include repatriated cases (e.g., cruises)?
include_repatriated = False

#Plot total numbers?
plot_total = True

#Additional settings
settings = {
    'log_y': False, #Use logarithmic y-axis?
    'condensed_plot': True, #Condensed plot? (small dots and narrow lines)
    'highlight_state': '', #Highlight state?
    'number_of_states': 20, #Limit number of states plotted?
}

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
        output = read_data.read_us(worldometers=worldometers)
        dates = output['dates']
        cases = output['cases']

#========================================================================================================
# Create plot based on type
#========================================================================================================

#Create figure
fig,ax = plt.subplots(figsize=(9,6),dpi=125)

#Total count
total_count = np.array([0.0 for i in cases['new york']['date']])
total_count_rp = np.array([0.0 for i in cases['new york']['date']])

#Iterate through every region
sorted_keys = [y[1] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
sorted_value = [y[0] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
for idx,(key,value) in enumerate(zip(sorted_keys,sorted_value)):
    
    #Total count
    total_count += np.array(cases[key][plot_type])
    
    #Special handling for Diamond Princess
    if include_repatriated == False and key in repatriated_locations: continue
    
    #Skip plotting if zero
    if value == 0: continue
    
    #How many states to plot?
    lim = 19
    if 'number_of_states' in settings.keys():
        lim = settings['number_of_states'] - 1
    if idx > lim: continue
    
    #Plot type
    if idx > 19:
        if 'highlight_state' in settings.keys() and settings['highlight_state'].lower() == key.lower():
            plt.plot(cases[key]['date'],cases[key][plot_type],'-o',zorder=100,linewidth=2.0,color='k',ms=4)
        else:
            plt.plot(cases[key]['date'],cases[key][plot_type],'-',zorder=1,linewidth=0.1,color='k')
    else:
        mtype = '--'; zord=2
        if np.nanmax(cases[key][plot_type]) > np.percentile(sorted_value,95): mtype = '-o'; zord=3
        zord = 54 - idx
        
        #Handle narrow plot
        kwargs = {}
        linewidth=1.0
        if 'condensed_plot' in settings.keys() and settings['condensed_plot'] == True:
            mtype = '-o'
            linewidth=0.5
            kwargs = {'ms':2}
            
        #Highlight individual state
        if 'highlight_state' in settings.keys() and settings['highlight_state'].lower() == key.lower():
            linewidth = 2.0; zord=100
            if 'ms' in kwargs.keys():
                kwargs['ms'] = 4
                kwargs['color'] = 'k'

        #Plot lines
        label_text = cases[key][plot_type][-1]
        if plot_type == "confirmed_normalized": label_text = "%0.1f"%(label_text)
        plt.plot(cases[key]['date'],cases[key][plot_type],mtype,zorder=zord,linewidth=linewidth,
                 label=f"{key.title()} ({label_text})",**kwargs)

#Plot total count
if plot_total == True and plot_type != "confirmed_normalized":
    plt.plot(cases[key]['date'],total_count,':',zorder=2,label=f'Total ({int(total_count[-1])})',color='k',linewidth=2)

#Format x-ticks
ax.set_xticks(cases[key]['date'][::7])
ax.set_xticklabels(cases[key]['date'][::7])
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%d'))

#Plot grid and legend
plt.grid()
plt.legend(loc=2,prop={'size':8})

#Plot title
title_string = {
    'confirmed':'Cumulative COVID-19 Confirmed Cases',
    'confirmed_normalized':'Cumulative COVID-19 Confirmed Cases',
    'deaths':'Cumulative COVID-19 Deaths',
    'recovered':'Cumulative COVID-19 Recovered Cases',
    'active':'Daily COVID-19 Active Cases',
    'daily':'Daily COVID-19 New Cases',
}
add_ylabel = " Per 100,000" if plot_type == "confirmed_normalized" else ""
add_title = "\n(Non-Repatriated Cases)" if include_repatriated == False else ""
plt.title(f"{title_string.get(plot_type)} {add_title}",fontweight='bold',loc='left')
plt.xlabel("Date",fontweight='bold')
plt.ylabel(f"Cases{add_ylabel}",fontweight='bold')

#Add logarithmic y-scale
if 'log_y' in settings.keys() and settings['log_y'] == True:
    plt.yscale('log')
    plt.ylim(bottom=1)

#Handle x-limit
if start_week > 5: start_week = 5
if start_week > 0:
    plt.xlim(left=dates[0]+dt.timedelta(hours=start_week*24*7))

#Plot attribution
add_title = f"\nLocations with {int(np.percentile(sorted_value,95))}+ total cases labeled with dots" if 'condensed_plot' in settings.keys() and settings['condensed_plot'] == True else ""

#Add data source
if worldometers == True:
    plt.title(f"Data from Johns Hopkins CSSE\nWorldometers From 18 March onward",loc='right',fontsize=8)
else:
    plt.title(f"Data from Johns Hopkins CSSE",loc='right',fontsize=8)

if plot_type == "active":
    plt.text(0.99,0.99,"\"Active\" cases = confirmed total - recovered - deaths",fontweight='bold',
             ha='right',va='top',transform=ax.transAxes,fontsize=8)

#Show plot and close
if save_image['setting'] == True:
    savepath = os.path.join(save_image['directory_path'],f"{plot_type}_chart_us.png")
    plt.savefig(savepath,bbox_inches='tight')
else:
    plt.show()
plt.close()

#Alert script is done
print("Done!")
