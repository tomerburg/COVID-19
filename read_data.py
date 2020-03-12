#Import packages & other scripts
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt

def read_us(negative_daily=True):

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
                    daily_change = cases["diamond princess"]['confirmed'][idx] - cases["diamond princess"]['confirmed'][idx-1]
                    if negative_daily == False and daily_change < 0: daily_change = 0
                    cases["diamond princess"]['daily'][idx] = daily_change
            
            #Handle Grand Princess cases separately
            elif "Grand Princess" in location:
                cases["grand princess"]['confirmed'][idx] += int(row['Confirmed'])
                cases["grand princess"]['deaths'][idx] += int(row['Deaths'])
                cases["grand princess"]['recovered'][idx] += int(row['Recovered'])
                cases["grand princess"]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
                if idx == 0:
                    cases["grand princess"]['daily'][idx] = np.nan
                else:
                    daily_change = cases["grand princess"]['confirmed'][idx] - cases["grand princess"]['confirmed'][idx-1]
                    if negative_daily == False and daily_change < 0: daily_change = 0
                    cases["grand princess"]['daily'][idx] = daily_change
                
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
                        daily_change = cases[state.lower()]['confirmed'][idx] - cases[state.lower()]['confirmed'][idx-1]
                        if negative_daily == False and daily_change < 0: daily_change = 0
                        cases[state.lower()]['daily'][idx] = daily_change
                
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
    
    return {'dates':dates,
            'dates_sites':dates_sites,
            'cases':cases,
            'cases_sites':cases_sites}

def read_world(negative_daily=True):
    
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

        #Iterate through every country
        for location,row in df.iterrows():
            
            #Fix for country name changes
            if location == 'Iran (Islamic Republic of)':
                location = "Iran"
            elif location in ['Republic of Korea','Korea, South']:
                location = "South Korea"
            elif location == 'Cruise Ship':
                location = "Others"
            elif location == 'China':
                location = "Mainland China"
            elif location == 'United Kingdom':
                location = "UK"
            elif location == 'occupied Palestinian territory':
                location = "Palestine"
            elif location in ['Taiwan*','Taipei and environs']:
                location = "Taiwan"
            elif location in ['Czechia']:
                location = "Czech Republic"

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
                daily_change = cases[location.lower()]['confirmed'][idx] - cases[location.lower()]['confirmed'][idx-1]
                if negative_daily == False and daily_change < 0: daily_change = 0
                cases[location.lower()]['daily'][idx] = daily_change

        #Increment date by 1 day
        start_date += dt.timedelta(hours=24)
    
    return {'dates':dates,
            'cases':cases}
