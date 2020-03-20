#Import packages & other scripts
import pickle
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt

def read_us(negative_daily=True,worldometers=False,save=False):

    #Construct list of dates with data available, through today
    start_date = dt.datetime(2020,1,22)
    iter_date = dt.datetime(2020,1,22)
    end_date = dt.datetime.today()
    dates = []
    while iter_date <= end_date:
        
        #Read in CSV file without worldometer
        if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
            strdate = iter_date.strftime("%m-%d-%Y")
            url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
            request = requests.get(url)
            if request.status_code == 200:
                dates.append(iter_date)
        
        #Use worldometers
        else:
            strdate = iter_date.strftime("%Y%m%d")
            if os.path.isfile(f"data/worldometers/us_{strdate}.csv") == True: dates.append(iter_date)
        
        #Increment date
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
        'VI':'Virgin Islands',
        'PR':'Puerto Rico',
    }
    
    #Read country population data
    pop_df = pd.read_csv("data/2019_us_population.csv")
    state_populations = {}
    for location,row in pop_df.iterrows():
        state_populations[row['State'].lower()] = int(row['Population'])

    #Create entry for each US state, along with Diamond Princess
    cases = {}
    inverse_state_abbr = {v: k for k, v in state_abbr.items()}
    for key in ['diamond princess','grand princess'] + [key.lower() for key in inverse_state_abbr.keys()]:
        cases[key] = {'date':dates,
                        'confirmed':[0 for i in range(len(dates))],
                        'confirmed_normalized':[0 for i in range(len(dates))],
                        'deaths':[0 for i in range(len(dates))],
                        'recovered':[0 for i in range(len(dates))],
                        'active':[0 for i in range(len(dates))],
                        'daily':[0 for i in range(len(dates))]}
    
    #Construct list of dates
    start_date = dates[0]
    end_date = dates[-1]
    while start_date <= end_date:

        #Read in CSV file without worldometer
        if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
            strdate = start_date.strftime("%m-%d-%Y")
            url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
            df = pd.read_csv(url)
            df = df.fillna(0) #replace NaNs with zero

            #Isolate cases to only those in US
            df_us = df.loc[df["Country/Region"] == "US"]
        
        #Read in CSV file with worldometer
        else:
            strdate = start_date.strftime("%Y%m%d")
            df_us = pd.read_csv(f"data/worldometers/us_{strdate}.csv")
            df_us = df_us.rename(columns={"State":"Province/State",
                                    "Total Cases":"Confirmed",
                                    "Total Deaths":"Deaths",
                                    "Total Recovered":"Recovered"})
            if 'puerto rico' in cases.keys(): del cases['puerto rico']
            if 'virgin islands' in cases.keys(): del cases['virgin islands']
            if 'diamond princess' in cases.keys(): del cases['diamond princess']
            if 'grand princess' in cases.keys(): del cases['grand princess']

        #Construct dict of all states
        dict_iter = []
        dict_used = []
        for _,row in df_us.iterrows():
            entry = {}
            
            dict_used.append(row['Province/State'].lower())
            entry['Province/State'] = row['Province/State']
            entry['Confirmed'] = row['Confirmed']
            entry['Deaths'] = row['Deaths']
            entry['Recovered'] = row['Recovered']
            
            #Account for incorrect entries
            #Source: Live update from Johns Hopkins CSSE from 0108 UTC
            if worldometers == False and start_date == dt.datetime(2020,3,18):
                df_updated = pd.read_csv("data/20200318_us.csv")
                dict_updated = {}
                for location,row2 in df_updated.iterrows():
                    dict_updated[row2['state'].lower()] = [row2['cases'],row2['deaths']]
                
                if row['Province/State'].lower() in dict_updated.keys():
                    entry['Confirmed'] = dict_updated.get(row['Province/State'].lower())[0]
                    entry['Deaths'] = dict_updated.get(row['Province/State'].lower())[1]
                
            dict_iter.append(entry)
        
        #Account for state discontinuities
        if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
            if start_date == dt.datetime(2020,3,14):
                #Source: https://covidtracking.com/notes/
                entry = {}
                dict_used.append('alaska')
                entry['Province/State'] = 'alaska'
                entry['Confirmed'] = 1
                entry['Deaths'] = 0
                entry['Recovered'] = 0
                dict_iter.append(entry)

        #Iterate through every US case
        for row in dict_iter:

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
                if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
                    if ',' in location:
                        abbr = (location.split(",")[1]).replace(" ","")
                        state = state_abbr.get(abbr)
                    else:
                        state = str(location)
                else:
                    state = str(location).lower()
                   
                #Virgin Islands handling
                if location == "Virgin Islands, U.S.":
                    state = "virgin islands"
                
                #Manually edit data points that are inaccurate due to CSSE server maintenance
                if start_date == dt.datetime(2020,3,13):
                    #Source: New York Times
                    correct_number = {
                        'new jersey':51,
                        'arkansas':9,
                        'colorado':77,
                    }
                    if state.lower() in correct_number.keys(): row['Confirmed'] = correct_number.get(state.lower())
                
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

        #Normalize count by population
        for key in cases.keys():
            
            #Get state's population data
            state_pop = int(state_populations.get(key.lower()))
            
            #Get index of date within list
            idx = dates.index(start_date)
            
            #Add case count per 100,000 people
            case_count = cases[key]['confirmed'][idx]
            cases[key]['confirmed_normalized'][idx] = (float(case_count) / float(state_pop)) * 100000
        
        #Increment date by 1 day
        start_date += dt.timedelta(hours=24)
    
    if save == True:
        cases['dates'] = dates
        with open('cases_us.pickle', 'wb') as f:
            pickle.dump(cases, f, pickle.HIGHEST_PROTOCOL)
    
    return {'dates':dates,
            'cases':cases,}

def read_world(negative_daily=True,worldometers=False,save=False):
    
    #Construct list of dates with data available, through today
    start_date = dt.datetime(2020,1,22)
    iter_date = dt.datetime(2020,1,22)
    end_date = dt.datetime.today()
    dates = []
    while iter_date <= end_date:
        
        #Don't use worldometers
        if worldometers == False or worldometers == True and iter_date < dt.datetime(2020,3,18):
            strdate = iter_date.strftime("%m-%d-%Y")
            url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{strdate}.csv'
            request = requests.get(url)
            if request.status_code == 200: dates.append(iter_date)
        
        #Use worldometers
        else:
            strdate = iter_date.strftime("%Y%m%d")
            if os.path.isfile(f"data/worldometers/world_{strdate}.csv") == True: dates.append(iter_date)
        
        #Increment date
        iter_date += dt.timedelta(hours=24)

    #Create entry for each US state, along with Diamond Princess
    cases = {}
    
    #Read country population data
    pop_df = pd.read_csv("data/2019_world_population.csv")
    population = {}
    for location,row in pop_df.iterrows():
        population[row['Country'].lower()] = row['Population']

    #Construct list of dates
    start_date = dates[0]
    end_date = dates[-1]
    while start_date <= end_date:

        #Read in CSV file without worldometer
        if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
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
        
        #Read in CSV file with worldometer
        else:
            strdate = start_date.strftime("%Y%m%d")
            df = pd.read_csv(f"data/worldometers/world_{strdate}.csv")
            df = df.rename(columns={"State":"Country/Region",
                                    "Total Cases":"Confirmed",
                                    "Total Deaths":"Deaths",
                                    "Total Recovered":"Recovered"})

        #Iterate through every country
        for location,row in df.iterrows():
            
            #Fix for country name changes
            if worldometers == False or worldometers == True and start_date < dt.datetime(2020,3,18):
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
                elif location in ['Hong Kong SAR']:
                    location = "Hong Kong"
                elif location in ['Viet Nam']:
                    location = "Vietnam"
                elif location == " Azerbaijan":
                    location = "Azerbaijan"
                elif location == "Republic of Ireland":
                    location = "Ireland"
                elif location == "Russian Federation":
                    location = "Russia"
            
            #Change country names for worldometers data
            else:
                swap_locs = {
                    "China":"Mainland China",
                    "USA":"US",
                    "S. Korea":"South Korea",
                    "Diamond Princess":"Others",
                    "Czechia":"Czech Republic",
                    "UAE":"United Arab Emirates",
                }
                location = row['Country/Region']
                if location in swap_locs.keys(): location = swap_locs.get(location)

            #Add entry for this region if previously non-existent
            if location.lower() not in cases.keys():
                cases[location.lower()] = {'date':dates,
                        'confirmed':[0 for i in range(len(dates))],
                        'confirmed_normalized':[0 for i in range(len(dates))],
                        'deaths':[0 for i in range(len(dates))],
                        'recovered':[0 for i in range(len(dates))],
                        'active':[0 for i in range(len(dates))],
                        'daily':[0 for i in range(len(dates))],
                        'daily_deaths':[0 for i in range(len(dates))]}

            #Get index of date within list
            idx = dates.index(start_date)
            
            #Manually edit data points that are inaccurate due to CSSE server maintenance
            #Source: https://www.worldometers.info/coronavirus/#countries
            if start_date == dt.datetime(2020,3,12):
                check_idx = dates.index(dt.datetime(2020,3,11))
                check_difference = abs(int(row['Confirmed']) - cases[location.lower()]['confirmed'][check_idx])
                if location.lower() == 'italy' and check_difference < 200:
                    row['Confirmed'] = 15113
                    row['Deaths'] = 1016
                    row['Recovered'] = 1258
                if location.lower() == 'france' and check_difference < 200:
                    row['Confirmed'] = 2876
                    row['Deaths'] = 61
                    row['Recovered'] = 12
                if location.lower() == 'spain' and check_difference < 200:
                    row['Confirmed'] = 3146
                    row['Deaths'] = 86
                    row['Recovered'] = 189
                if location.lower() == 'germany' and check_difference < 200:
                    row['Confirmed'] = 2745
                    row['Deaths'] = 6
                    row['Recovered'] = 25
            if start_date == dt.datetime(2020,3,18) and worldometers == False:
                if location.lower() == 'spain':
                    row['Confirmed'] = 14769
                if location.lower() == 'us':
                    row['Confirmed'] = 9241

            cases[location.lower()]['confirmed'][idx] += int(row['Confirmed'])
            cases[location.lower()]['deaths'][idx] += int(row['Deaths'])
            cases[location.lower()]['recovered'][idx] += int(row['Recovered'])
            cases[location.lower()]['active'][idx] += int(row['Confirmed']) - int(row['Recovered']) - int(row['Deaths'])
            if idx == 0:
                cases[location.lower()]['daily'][idx] = np.nan
                cases[location.lower()]['daily_deaths'][idx] = np.nan
            elif location.lower() == 'mainland china' and strdate == '02-13-2020':
                cases[location.lower()]['daily'][idx] = np.nan
                cases[location.lower()]['daily_deaths'][idx] = np.nan
            else:
                daily_change = cases[location.lower()]['confirmed'][idx] - cases[location.lower()]['confirmed'][idx-1]
                if negative_daily == False and daily_change < 0: daily_change = 0
                cases[location.lower()]['daily_deaths'][idx] = daily_change
                
                daily_change = cases[location.lower()]['deaths'][idx] - cases[location.lower()]['deaths'][idx-1]
                if negative_daily == False and daily_change < 0: daily_change = 0
                cases[location.lower()]['daily_deaths'][idx] = daily_change
                
        #Normalize count by population
        for key in cases.keys():
            
            #Get index of date within list
            idx = dates.index(start_date)
            
            #If population data can be found for this country:
            if key.lower() in population.keys():
                
                #Get country population data
                country_pop = population.get(key.lower())
                
                #Add case count per 100,000 people
                case_count = cases[key]['confirmed'][idx]
                cases[key]['confirmed_normalized'][idx] = (float(case_count) / float(country_pop)) * 100000
            
            else:
                
                #Otherwise, add nan
                cases[key]['confirmed_normalized'][idx] = 0.0

        #Increment date by 1 day
        start_date += dt.timedelta(hours=24)
    
    if save == True:
        cases['dates'] = dates
        with open('cases_world.pickle', 'wb') as f:
            pickle.dump(cases, f, pickle.HIGHEST_PROTOCOL)
    
    return {'dates':dates,
            'cases':cases}
