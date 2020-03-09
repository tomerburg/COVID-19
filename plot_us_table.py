#Import packages & other scripts
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from color_gradient import Gradient

#========================================================================================================
# User-defined settings
#========================================================================================================

#Report date(s) to plot
plot_start_date = dt.datetime(2020,1,22)
plot_end_date = dt.datetime(2020,3,7)

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, deaths, recovered, active, daily)
plot_type = "confirmed"

#Include repatriated cases (e.g., cruises)?
include_repatriated = False

#Plot total numbers?
plot_total = True

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

    #Construct list of dates with data available, through today
    start_date = dt.datetime(2020,1,22)
    iter_date = dt.datetime(2020,1,22)
    end_date = dt.datetime.today()
    dates = []
    dates_sites = []
    while iter_date <= end_date:
        strdate = iter_date.strftime("%m-%d-%Y")
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
        request = requests.get(url)
        if request.status_code == 200:
            dates.append(iter_date)
            if iter_date >= dt.datetime(2020,3,1): dates_sites.append(iter_date)
        iter_date += dt.timedelta(hours=24)

    #US states list
    state_abbr = {
        'AL':'Alabama',
        'AK':'Alaska',
        'AZ':'Arizona',
        'AR':'Arkansas',
        'CA':'California',
        'CO':'Colorado',
        'CT':'Connecticut',
        'DE':'Delaware',
        'D.C.':'District of Columbia',
        'FL':'Florida',
        'GA':'Georgia',
        'HI':'Hawaii',
        'ID':'Idaho',
        'IL':'Illinois',
        'IN':'Indiana',
        'IA':'Iowa',
        'KS':'Kansas',
        'KY':'Kentucky',
        'LA':'Louisiana',
        'ME':'Maine',
        'MD':'Maryland',
        'MA':'Massachusetts',
        'MI':'Michigan',
        'MN':'Minnesota',
        'MS':'Mississippi',
        'MO':'Missouri',
        'MT':'Montana',
        'NE':'Nebraska',
        'NV':'Nevada',
        'NH':'New Hampshire',
        'NJ':'New Jersey',
        'NM':'New Mexico',
        'NY':'New York',
        'NC':'North Carolina',
        'ND':'North Dakota',
        'OH':'Ohio',
        'OK':'Oklahoma',
        'OR':'Oregon',
        'PA':'Pennsylvania',
        'RI':'Rhode Island',
        'SC':'South Carolina',
        'SD':'South Dakota',
        'TN':'Tennessee',
        'TX':'Texas',
        'UT':'Utah',
        'VT':'Vermont',
        'VA':'Virginia',
        'WA':'Washington',
        'WV':'West Virginia',
        'WI':'Wisconsin',
        'WY':'Wyoming',
    }

    #Create entry for each US state, along with Diamond Princess
    cases = {}
    inverse_state_abbr = {v: k for k, v in state_abbr.items()}
    for key in ['diamond princess','grand princess'] + [key.lower() for key in inverse_state_abbr.keys()]:
        cases[key] = {'date':dates,
                        'confirmed':[0 for i in range(len(dates))],
                        'deaths':[0 for i in range(len(dates))],
                        'recovered':[0 for i in range(len(dates))],
                        'active':[0 for i in range(len(dates))],
                        'daily':[0 for i in range(len(dates))]}

    #Add individual location sites for plotting dots
    cases_sites = {}
    
    #Construct list of dates
    start_date = dates[0]
    end_date = dates[-1]
    while start_date <= end_date:

        #Read in CSV file
        strdate = start_date.strftime("%m-%d-%Y")
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
        df = pd.read_csv(url)
        df = df.fillna(0) #replace NaNs with zero

        #Isolate cases to only those in US
        df_us = df.loc[df["Country/Region"] == "US"]

        #Iterate through every US case
        for _,row in df_us.iterrows():

            #Get state/province name
            location = row['Province/State']

            #Get index of date within list
            idx = dates.index(start_date)
            
            #Special handling for 2/21/2020
            if start_date.strftime("%Y%m%d") == "20200221":
                if "Lackland, TX" in location or "Travis, CA" in location or "Ashland, NE" in location:
                    location = location + "(Diamond Princess)"

            #Handle Diamond Princess cases separately
            if "Diamond Princess" in location:
                cases["diamond princess"]['confirmed'][idx] += int(row['Confirmed'])
                cases["diamond princess"]['deaths'][idx] += int(row['Deaths'])
                cases["diamond princess"]['recovered'][idx] += int(row['Recovered'])
                cases["diamond princess"]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
                if idx == 0:
                    cases["diamond princess"]['daily'][idx] = np.nan
                else:
                    cases["diamond princess"]['daily'][idx] = cases["diamond princess"]['confirmed'][idx] - cases["diamond princess"]['confirmed'][idx-1]
            
            #Handle Grand Princess cases separately
            elif "Grand Princess" in location:
                cases["grand princess"]['confirmed'][idx] += int(row['Confirmed'])
                cases["grand princess"]['deaths'][idx] += int(row['Deaths'])
                cases["grand princess"]['recovered'][idx] += int(row['Recovered'])
                cases["grand princess"]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
                if idx == 0:
                    cases["grand princess"]['daily'][idx] = np.nan
                else:
                    cases["grand princess"]['daily'][idx] = cases["grand princess"]['confirmed'][idx] - cases["grand princess"]['confirmed'][idx-1]
                
            #Otherwise, handle states
            else:
                #Handle state abbreviation vs. full state name
                if ',' in location:
                    abbr = (location.split(",")[1]).replace(" ","")
                    state = state_abbr.get(abbr)
                else:
                    state = str(location)

                #Add cases to entry for this state & day
                if state.lower() in cases.keys():
                    cases[state.lower()]['confirmed'][idx] += int(row['Confirmed'])
                    cases[state.lower()]['deaths'][idx] += int(row['Deaths'])
                    cases[state.lower()]['recovered'][idx] += int(row['Recovered'])
                    cases[state.lower()]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
                    if idx == 0:
                        cases[state.lower()]['daily'][idx] = np.nan
                    else:
                        cases[state.lower()]['daily'][idx] = cases[state.lower()]['confirmed'][idx] - cases[state.lower()]['confirmed'][idx-1]
                
                #Add individual sites
                if start_date >= dt.datetime(2020,3,1):
                    idx_sites = dates_sites.index(start_date)
                    if location not in cases_sites.keys():
                        cases_sites[location] = {'date':dates_sites,
                            'confirmed':[0 for i in range(len(dates_sites))],
                            'deaths':[0 for i in range(len(dates_sites))],
                            'recovered':[0 for i in range(len(dates_sites))],
                            'active':[0 for i in range(len(dates_sites))],
                            'daily':[0 for i in range(len(dates_sites))],
                            'latitude':(float(row['Latitude'])),
                            'longitude':(float(row['Longitude']))}
                    cases_sites[location]['confirmed'][idx_sites] = int(row['Confirmed'])
                    cases_sites[location]['deaths'][idx_sites] = int(row['Deaths'])
                    cases_sites[location]['recovered'][idx_sites] = int(row['Recovered'])
                    cases_sites[location]['active'][idx_sites] = int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
                    if idx_sites == 0:
                        cases_sites[location]['daily'][idx_sites] = np.nan
                    else:
                        cases_sites[location]['daily'][idx_sites] = cases_sites[location]['confirmed'][idx_sites] - cases_sites[location]['confirmed'][idx_sites-1]


        #Increment date by 1 day
        start_date += dt.timedelta(hours=24)

#========================================================================================================
# Create plot based on type
#========================================================================================================

#Function for returning number within range
def return_val(start_range,end_range,start_size,end_size,val):
    frac = (val-start_range)/(end_range-start_range)
    frac = (frac * (end_size-start_size)) + start_size
    return frac

#Total count
total_count = np.array([0.0 for i in cases['diamond princess']['date']])
total_count_row = np.array([0.0 for i in cases['diamond princess']['date']])

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
                     [['#FFFF00',0.9],['#EE7B51',int(max_val*0.3)]],
                     [['#EE7B51',int(max_val*0.3)],['#B53079',int(max_val*0.6)]],
                     [['#B53079',int(max_val*0.6)],['#070092',int(max_val*0.9)]],
                     [['#070092',int(max_val*0.9)],['#000000',int(max_val*1.2)]])

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
