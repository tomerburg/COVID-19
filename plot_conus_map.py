#Import packages & other scripts
import pickle
import os, sys
import requests
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

import read_data
from cartopy_wrapper import Map
from color_gradient import Gradient

#========================================================================================================
# User-defined settings
#========================================================================================================

#Report date(s) to plot
plot_start_date = dt.datetime(2020,3,19)
plot_end_date = dt.datetime(2020,3,19)
plot_today_only = True #If true, overrides previous dates

#Use blue marble background for the map. "directory_path" string is ignored if setting==False.
# ** "directory_path" must be a folder with an image and an "images.json" file, in accordance with Cartopy's ax.background_img() function:
# ** https://scitools.org.uk/cartopy/docs/v0.15/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.background_img
# ** A Blue Marble image and directory are included in this repository.
background_image = {'setting': False,
                    'directory_path': "full_directory_path_here"}

#Whether to save image or display. "directory_path" string is ignored if setting==False.
save_image = {'setting': False,
              'directory_path': "full_directory_path_here"}

#What to plot (confirmed, confirmed_normalized, deaths, recovered, active, daily)
plot_type = "confirmed"

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
    
    if plot_today_only == True:
        plot_start_date = dates[-1]
        plot_end_date = dates[-1]

#========================================================================================================
# Handle map projection & geography
#========================================================================================================

#Function for returning number within range
def return_val(start_range,end_range,start_size,end_size,val):
    frac = (val-start_range)/(end_range-start_range)
    frac = (frac * (end_size-start_size)) + start_size
    return frac

#Create data colortable
max_val = 0.0
if plot_type == 'confirmed_normalized':
    for key in [k for k in cases.keys() if k not in ['diamond princess','grand princess']]:
        max_val = cases[key]['confirmed_normalized'][-1] if cases[key]['confirmed_normalized'][-1] > max_val else max_val
    if max_val < 20: max_val = 20
else:
    for key in [k for k in cases.keys()]:
        for ptype in ['confirmed','confirmed_normalized','deaths','recovered','active','daily']:
            max_val = cases[key][ptype][-1] if cases[key][ptype][-1] > max_val else max_val
    if max_val < 40: max_val = 40

color_obj = Gradient([['#FFFF00',1.0],['#EE7B51',round(max_val*0.15)]],
               [['#EE7B51',round(max_val*0.15)],['#B53079',round(max_val*0.6)]],
               [['#B53079',round(max_val*0.6)],['#070092',round(max_val*1.2)]])

#Create Cartopy projection
try:
    m
except:
    lon1 = -99.0
    lat1 = 35.0
    slat = 35.0
    bound_n = 50.0
    bound_s = 21.5
    bound_w = -122.0
    bound_e = -72.5
    m = Map('LambertConformal',central_longitude=lon1,central_latitude=lat1,standard_parallels=[slat],res='h')
    proj = m.proj

#Read in US states shapefile
try:
    shp
except:
    fname = r'cb_2018_us_state_500k/cb_2018_us_state_500k.shp'
    shp = Reader(fname)
    print("--> Read in US states shapefile")

#Iterate through dates
while plot_start_date <= plot_end_date:
    
    #Update on current date
    print(f"------> Report date {plot_start_date}")
    
    #Create figure
    fig = plt.figure(figsize=(14,9),dpi=125)
    ax = plt.axes(projection=proj)
    ax.set_extent([bound_w,bound_e,bound_s,bound_n])
    print("--> Created matplotlib figure & map projection")

    #Draw map background
    if background_image['setting'] == True:
        print("--> Starting to read in blue marble image")
        os.environ["CARTOPY_USER_BACKGROUNDS"] = background_image['directory_path']
        ax.background_img(name='BM', resolution='low')
        background_image['alpha'] = 0.5
        print("--> Plotted blue marble image")
    else:
        background_image['alpha'] = 1.0

    #Draw geography
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    print("--> Plotted geographic & political boundaries")

    #========================================================================================================
    # Plot data
    #========================================================================================================

    #Iterate through all states
    total_cases = 0
    for record, state in zip(shp.records(), shp.geometries()):

        #Reference state name as a separate variable
        name = record.attributes['NAME']
        
        #Get state's case data for this date
        if name.lower() in cases.keys():
            idx = cases[name.lower()]['date'].index(plot_start_date)
            if plot_type not in ['confirmed','confirmed_normalized','deaths','recovered','active','daily']: plot_type = 'confirmed'
            case_number = cases[name.lower()][plot_type][idx]
            total_cases += case_number
        else:
            continue

        #Exclude states outside of CONUS & territories from map, but include in case count
        if name.lower() in ['alaska','hawaii','guam','puerto rico','commonwealth of the northern mariana islands',
                                                'american samoa','united states virgin islands']: continue

        #------------------------------------------------------------------------------------

        #Set background state color
        if case_number > 0:
            cmap = color_obj.get_cmap([case_number])
            facecolor = color_obj.colors[0]
        else:
            facecolor = '#eeeeee'

        #Draw states
        ax.add_geometries([state], ccrs.PlateCarree(), facecolor=facecolor, edgecolor='black', linewidth=0.5,
                          alpha=background_image['alpha'])

        #------------------------------------------------------------------------------------

        #Format case number as a string
        case_str = str(case_number)
        if "." in case_str: case_str = '%0.1f'%(case_number)
        if case_number == 0: case_str = " - "

        #Label case number using state centroid
        centroid = state.centroid.bounds
        lon = centroid[0]; lat = centroid[1]

        #Adjust certain states to make plotting nicer
        if name == "Louisiana": lon = lon - 0.5
        if name == "Florida": lon = lon + 0.7
        if name == "California": lat = lat - 1.0
        if name == "Maryland":
            lon = lon - 0.1; lat = lat + 0.2
        if name == "Michigan":
            lon = lon + 0.5; lat = lat - 0.5
        if name in ['Delaware','Rhode Island']:
            lon = lon - 0.1

        #For some states, use arrows instead of direct labels
        state_transform = {
            'New Jersey':(2.0,-0.7),
            'Delaware':(2.5,-0.5),
            'Maryland':(3.2,-1.8),
            'Rhode Island':(1.5,-1.5),
            'District of Columbia':(3.0,-3.0),
        }
        ncolor = 'k' if background_image['alpha'] == 1 else 'w'
        if ncolor == 'k' and case_number > (max_val*0.8): ncolor = 'w'
        if name in state_transform.keys():
            transform = ccrs.PlateCarree()._as_mpl_transform(ax)
            x_tr, y_tr = state_transform.get(name)
            ax.annotate(case_str,
                        xy=(lon,lat), xycoords=transform,
                        xytext=(lon+x_tr,lat+y_tr), 
                        fontweight='bold', ha='center', va='center', color=ncolor, fontsize=12,
                        arrowprops=dict(arrowstyle="->",
                                        shrinkA=0, shrinkB=0,
                                        connectionstyle="arc3", 
                                        color=ncolor),
                        transform=ccrs.PlateCarree(), zorder=3)
        else:
            ax.text(lon, lat, case_str, color='k', fontsize=12,
                    fontweight='bold', ha='center', va='center', transform=ccrs.PlateCarree(), zorder=3)

    #Add plot type and labels
    plot_name = {
        'confirmed':'Confirmed Cases',
        'confirmed_normalized':'Confirmed Cases\nPer 100,000 People',
        'deaths':'Death Count',
        'recovered':'Recovered Cases',
        'active':'Active Confirmed Cases',
        'daily':'New Daily Cases'
    }
    plt.title(f"CONUS States COVID-19 {plot_name.get(plot_type)}",fontweight='bold',fontsize=18,loc='left')
    add_label = 'as of' if plot_type in ['active','daily'] else 'through'
    plt.title(f"Cases {add_label} {plot_start_date.strftime('%d %B %Y')}",fontweight='bold',fontsize=14,loc='right')

    #Label data source
    if worldometers == False or worldometers == True and plot_start_date < dt.datetime(2020,3,18):
        plt.text(0.99,0.01,'Data from Johns Hopkins CSSE:\nhttps://github.com/CSSEGISandData/COVID-19',
                 ha='right',va='bottom',transform=ax.transAxes,fontsize=11,color='white',fontweight='bold')
    else:
        plt.text(0.99,0.01,'Data from Worldometers:\nhttps://www.worldometers.info/coronavirus/',
                 ha='right',va='bottom',transform=ax.transAxes,fontsize=11,color='white',fontweight='bold')

    #Label total number of cases
    if plot_type != 'confirmed_normalized':
        if worldometers == False:
            dp_cases = cases['diamond princess'][plot_type][idx]
            gp_cases = cases['grand princess'][plot_type][idx]
            other_cases = dp_cases + gp_cases
            title_string = f'Repatriated Cases: {other_cases}\n\nTotal US Cases: {total_cases}\nTotal US Cases (With Repatriated): {total_cases+other_cases}'
        else:
            title_string = f'Total US Cases: {total_cases}'
        plt.text(0.01,0.01,title_string,
                 ha='left',va='bottom',transform=ax.transAxes,fontsize=11,color='w',fontweight='bold',bbox={'facecolor':'k', 'alpha':0.4, 'boxstyle':'round'})

    #Save image?
    if save_image['setting'] == True:
        savepath = os.path.join(save_image['directory_path'],f"{plot_type}_{plot_start_date.strftime('%Y%m%d')}.png")
        plt.savefig(savepath,bbox_inches='tight')
    else:
        plt.show()
    plt.close()
    
    #Increment date
    plot_start_date += dt.timedelta(hours=24)

#Alert script is done
print("Done!")
