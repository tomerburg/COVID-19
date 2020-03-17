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
        'VI':'Virgin Islands',
        'PR':'Puerto Rico',
    }
    
    #US states list
    state_populations = {
        'Alabama':'4,903,185',
        'Alaska':'731,545',
        'Arizona':'7,278,717',
        'Arkansas':'3,017,825',
        'California':'39,512,223',
        'Colorado':'5,758,736',
        'Connecticut':'3,565,287',
        'Delaware':'973,764',
        'District Of Columbia':'705,749',
        'Florida':'21,477,737',
        'Georgia':'10,617,423',
        'Hawaii':'1,415,872',
        'Idaho':'1,787,147',
        'Illinois':'12,671,821',
        'Indiana':'6,732,219',
        'Iowa':'3,155,070',
        'Kansas':'2,913,314',
        'Kentucky':'4,467,673',
        'Louisiana':'4,648,794',
        'Maine':'1,344,212',
        'Maryland':'6,045,680',
        'Massachusetts':'6,949,503',
        'Michigan':'9,986,857',
        'Minnesota':'5,639,632',
        'Mississippi':'2,976,149',
        'Missouri':'6,137,428',
        'Montana':'1,068,778',
        'Nebraska':'1,934,408',
        'Nevada':'3,080,156',
        'New Hampshire':'1,359,711',
        'New Jersey':'8,882,190',
        'New Mexico':'2,096,829',
        'New York':'19,453,561',
        'North Carolina':'10,488,084',
        'North Dakota':'762,062',
        'Ohio':'11,689,100',
        'Oklahoma':'3,956,971',
        'Oregon':'4,217,737',
        'Pennsylvania':'12,801,989',
        'Rhode Island':'1,059,361',
        'South Carolina':'5,148,714',
        'South Dakota':'884,659',
        'Tennessee':'6,833,174',
        'Texas':'28,995,881',
        'Utah':'3,205,958',
        'Vermont':'623,989',
        'Virginia':'8,535,519',
        'Washington':'7,614,893',
        'West Virginia':'1,792,065',
        'Wisconsin':'5,822,434',
        'Wyoming':'578,759',
        'Virgin Islands':'104,914',
        'Puerto Rico':'3,193,694',
        'Diamond Princess':'3000',
        'Grand Princess':'3000',
    }

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
            dict_iter.append(entry)
        
        #Account for state discontinuities
        if start_date == dt.datetime(2020,3,14):
            #Source: https://covidtracking.com/notes/
            entry = {}
            dict_used.append('alaska')
            entry['Province/State'] = 'alaska'
            entry['Confirmed'] = 1
            entry['Deaths'] = 0
            entry['Recovered'] = 0
            dict_iter.append(entry)
        
        """
        for key in [k for k in cases.keys() if k not in ['diamond princess','grand princess']]:
            if key not in dict_used:
                entry = {}
                idx = dates.index(start_date)
                entry['Province/State'] = key
                entry['Confirmed'] = 0
                entry['Deaths'] = 0
                entry['Recovered'] = 0
                dict_iter.append(entry)
        """

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
                if ',' in location:
                    abbr = (location.split(",")[1]).replace(" ","")
                    state = state_abbr.get(abbr)
                else:
                    state = str(location)
                   
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
            state_pop = int((state_populations.get(key.title())).replace(",",""))
            
            #Get index of date within list
            idx = dates.index(start_date)
            
            #Add case count per 100,000 people
            case_count = cases[key]['confirmed'][idx]
            cases[key]['confirmed_normalized'][idx] = (float(case_count) / float(state_pop)) * 100000
        
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
