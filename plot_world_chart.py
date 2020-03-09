#Import packages & other scripts
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#========================================================================================================
# User-defined settings
#========================================================================================================

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, deaths, recovered, active, daily)
plot_type = "confirmed"

#Include Mainland China?
mainland_china = True

#Plot total numbers?
plot_total = True

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
    #Construct list of dates with data available, through today
    start_date = dt.datetime(2020,1,22)
    iter_date = dt.datetime(2020,1,22)
    end_date = dt.datetime.today()
    dates = []
    while iter_date <= end_date:
        strdate = iter_date.strftime("%m-%d-%Y")
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
        request = requests.get(url)
        if request.status_code == 200: dates.append(iter_date)
        iter_date += dt.timedelta(hours=24)

    #Create entry for each US state, along with Diamond Princess
    cases = {}

    #Construct list of dates
    start_date = dates[0]
    end_date = dates[-1]
    while start_date <= end_date:

        #Read in CSV file
        strdate = start_date.strftime("%m-%d-%Y")
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
        df = pd.read_csv(url)
        df = df.fillna(0) #replace NaNs with zero

        #sum by country
        cols = (df.columns).tolist()
        if 'Last Update' in cols: df = df.drop(columns=['Last Update'])
        if 'Latitude' in cols: df = df.drop(columns=['Latitude'])
        if 'Longitude' in cols: df = df.drop(columns=['Longitude'])
        df = df.groupby('Country/Region').sum()

        #Iterate through every US case
        for location,row in df.iterrows():

            #Add entry for this region if previously non-existent
            if location.lower() not in cases.keys():
                cases[location.lower()] = {'date':dates,
                        'confirmed':[0 for i in range(len(dates))],
                        'deaths':[0 for i in range(len(dates))],
                        'recovered':[0 for i in range(len(dates))],
                        'active':[0 for i in range(len(dates))],
                        'daily':[0 for i in range(len(dates))]}

            #Get index of date within list
            idx = dates.index(start_date)

            cases[location.lower()]['confirmed'][idx] += int(row['Confirmed'])
            cases[location.lower()]['deaths'][idx] += int(row['Deaths'])
            cases[location.lower()]['recovered'][idx] += int(row['Recovered'])
            cases[location.lower()]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
            if idx == 0:
                cases[location.lower()]['daily'][idx] = np.nan
            elif location.lower() == 'mainland china' and strdate == '02-13-2020':
                cases[location.lower()]['daily'][idx] = np.nan
            else:
                cases[location.lower()]['daily'][idx] = cases[location.lower()]['confirmed'][idx] - cases[location.lower()]['confirmed'][idx-1]

        #Increment date by 1 day
        start_date += dt.timedelta(hours=24)

#========================================================================================================
# Create plot based on type
#========================================================================================================

#Create figure
fig,ax = plt.subplots(figsize=(9,6),dpi=125)

#Total count
total_count = np.array([0.0 for i in cases['mainland china']['date']])
total_count_row = np.array([0.0 for i in cases['mainland china']['date']])

#Iterate through every region
sorted_keys = [y[1] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
sorted_value = [y[0] for y in sorted([(np.nanmax(cases[x][plot_type]), x) for x in cases.keys()])][::-1]
for idx,(key,value) in enumerate(zip(sorted_keys,sorted_value)):

    #Special handling for China
    if mainland_china == False and key == 'mainland china': continue
    
    #Total count
    total_count += np.array(cases[key][plot_type])
    if key != 'mainland china': total_count_row += np.array(cases[key][plot_type])
    
    #Skip plotting if zero
    if value == 0: continue
    
    #Plot type
    if idx > 19:
        plt.plot(cases[key]['date'],cases[key][plot_type],':',linewidth=0.5,color='k',zorder=1)
    else:
        mtype = '--'; zord=2
        if np.nanmax(cases[key][plot_type]) > np.percentile(sorted_value,95): mtype = '-o'; zord=3

        #Handle US & UK titles
        loc = key.title()
        if key in ['us','uk']: loc = key.upper()

        #Plot lines
        plt.plot(cases[key]['date'],cases[key][plot_type],mtype,zorder=zord,label=f"{loc} ({cases[key][plot_type][-1]})")

#Plot total count
if plot_total == True:
    plt.plot(cases[key]['date'],total_count,':',zorder=2,label=f'Total ({int(total_count[-1])})',color='k',linewidth=2)
    if mainland_china == True: plt.plot(cases[key]['date'],total_count_row,':',zorder=2,label=f'Total ROW ({int(total_count_row[-1])})',color='b',linewidth=2)

#Format x-ticks
ax.set_xticks(cases[key]['date'][::7])
ax.set_xticklabels(cases[key]['date'][::7])
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

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
}
add_title = "\n(Non-Mainland China)" if mainland_china == False else ""
plt.title(f"{title_string.get(plot_type)} {add_title}",fontweight='bold',loc='left')
plt.xlabel("Date",fontweight='bold')
plt.ylabel("Cases",fontweight='bold')

#Plot attribution
plt.title(f'Data from Johns Hopkins CSSE\nLocations with {int(np.percentile(sorted_value,95))}+ total cases labeled with dots',
          loc='right',fontsize=8)
if plot_type == "active":
    plt.text(0.99,0.99,"\"Active\" cases = confirmed total - recovered - deaths",fontweight='bold',
             ha='right',va='top',transform=ax.transAxes,fontsize=8)
plt.text(0.27,0.98,"Top 20 locations plotted",
             ha='left',va='top',transform=ax.transAxes,fontsize=8)

#Show plot and close
if save_image['setting'] == True:
    savepath = os.path.join(save_image['directory_path'],f"{plot_type}_chart.png")
    plt.savefig(savepath,bbox_inches='tight')
else:
    plt.show()
plt.close()

#Alert script is done
print("Done!")
