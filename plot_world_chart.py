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

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, deaths, recovered, active, daily, daily_deaths)
plot_type = "confirmed"

#Include Mainland China?
mainland_china = True

#Plot total numbers?
plot_total = True

#Plot confirmed vs. recoveries?
plot_versus = False

#Additional settings
settings = {
    'log_y': False, #Use logarithmic y-axis?
    'condensed_plot': True, #Condensed plot? (small dots and narrow lines)
    'highlight_country': 'US', #Highlight country?
    'number_of_countries': 20, #Limit number of countries plotted?
}

#Whether to use data from Worldometers from March 18th onwards
worldometers = True

#Read from local file? (WARNING = ensure data sources are the same!)
read_from_local = False

#========================================================================================================
# Get COVID-19 case data
#========================================================================================================

"""
COVID-19 case data is retrieved from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19
"""

#Avoid re-reading case data if it's already stored in memory
try:
    cases
except:
    
    if read_from_local == True:
        cases = pickle.load(open('cases_world.pickle','rb'))
        dates = cases['dates']
        del cases['dates']
    else:
        output = read_data.read_world(worldometers=worldometers)
        dates = output['dates']
        cases = output['cases']

#========================================================================================================
# Create plot based on type
#========================================================================================================

#Create figure
fig,ax = plt.subplots(figsize=(9,6),dpi=125)

#Total count
key_0 = [k for k in cases.keys()][0]
total_count = np.array([0.0 for i in cases[key_0]['date']])
total_count_row = np.array([0.0 for i in cases[key_0]['date']])

#Iterate through every region
sorted_keys = [y[1] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
sorted_value = [y[0] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
for idx,(key,value) in enumerate(zip(sorted_keys,sorted_value)):

    #Special handling for China
    if mainland_china == False and key == 'mainland china': continue
    
    #Total count
    total_count += np.array(cases[key][plot_type])
    if plot_versus == True:
        total_count_row += np.array(cases[key]['recovered'])
        continue
    if key != 'mainland china': total_count_row += np.array(cases[key][plot_type])
        
    #Skip plotting if zero
    if value == 0: continue
    
    #How many countries to plot?
    lim = 19
    if 'number_of_countries' in settings.keys():
        lim = settings['number_of_countries'] - 1
    if lim > 19: lim = 19
    
    #Plot type
    if idx > lim:
        pass
    else:
        mtype = '--'; zord=2
        if np.nanmax(cases[key][plot_type]) > np.percentile(sorted_value,95): mtype = '-o'; zord=3
        zord = 22 - idx

        #Handle US & UK titles
        loc = key.title()
        if key in ['us','uk']: loc = key.upper()
        
        #Handle narrow plot
        kwargs = {}
        linewidth=1.0
        if 'condensed_plot' in settings.keys() and settings['condensed_plot'] == True:
            mtype = '-o'
            linewidth=0.5
            kwargs = {'ms':2}
            
        #Highlight individual country
        if 'highlight_country' in settings.keys() and settings['highlight_country'].lower() == key.lower():
            linewidth = 2.0
            if 'ms' in kwargs.keys():
                kwargs['ms'] = 4; zord=50; kwargs['color'] = 'k'
        
        #Plot lines
        plt.plot(cases[key]['date'],cases[key][plot_type],mtype,zorder=zord,linewidth=linewidth,
                 label=f"{loc} ({cases[key][plot_type][-1]})",**kwargs)

#Plot total count
if plot_total == True:
    plt.plot(cases[key]['date'],total_count,':',zorder=50,label=f'Total ({int(total_count[-1])})',color='k',linewidth=2)
    if plot_versus == True:
        plt.plot(cases[key]['date'],total_count_row,':',zorder=2,label=f'Total Recoveries ({int(total_count_row[-1])})',color='b',linewidth=2)
    elif mainland_china == True:
        plt.plot(cases[key]['date'],total_count_row,':',zorder=2,label=f'Total ROW ({int(total_count_row[-1])})',color='b',linewidth=2)
    
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
    'deaths':'Cumulative COVID-19 Deaths',
    'recovered':'Cumulative COVID-19 Recovered Cases',
    'active':'Daily COVID-19 Active Cases',
    'daily':'Daily COVID-19 New Cases',
    'daily_deaths':'Daily COVID-19 New Deaths',
}
add_title = "\n(Non-Mainland China)" if mainland_china == False else ""
plt.title(f"{title_string.get(plot_type)} {add_title}",fontweight='bold',loc='left')
plt.xlabel("Date",fontweight='bold')
plt.ylabel("Cases",fontweight='bold')

#Add logarithmic y-scale
if 'log_y' in settings.keys() and settings['log_y'] == True:
    plt.yscale('log')
    plt.ylim(bottom=1)

#Add data source
if worldometers == True:
    plt.title(f"Data from Johns Hopkins CSSE\nWorldometers From 18 March onward",loc='right',fontsize=8)
else:
    plt.title(f"Data from Johns Hopkins CSSE",loc='right',fontsize=8)

if plot_type == "active":
    plt.text(0.99,0.99,"\"Active\" cases = confirmed total - recovered - deaths",fontweight='bold',
             ha='right',va='top',transform=ax.transAxes,fontsize=8)
#plt.text(0.27,0.98,"Top 20 locations plotted",ha='left',va='top',transform=ax.transAxes,fontsize=8)

#Show plot and close
if save_image['setting'] == True:
    savepath = os.path.join(save_image['directory_path'],f"{plot_type}_chart_world.png")
    plt.savefig(savepath,bbox_inches='tight')
else:
    plt.show()
plt.close()

#Alert script is done
print("Done!")
