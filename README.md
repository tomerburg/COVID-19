# COVID-19
A collection of Python scripts to visualize real-time COVID-19 data from Johns Hopkins CSSE.

## Installation
Clone this repository using the following command:
```
git clone https://github.com/tomerburg/COVID-19
```

## Dependencies
The following packages are used in plotting scripts:
- Python 3.6 or newer
- Cartopy
- MetPy
- Pandas

## Data and Caveats
This repository contains scripts that visualize real-time COVID-19 data from Johns Hopkins CSSE:
https://github.com/CSSEGISandData/COVID-19

Data from this source are limited to the same constraints and terms of use as posted on the CSSE GIS and Data GitHub page. Specifically, the count of confirmed cases is an under-estimate of the actual case count which is unknown. As such, calculations of Case Fatality Rate (CFR) are not provided with these scripts in this repository. Assuming that there are many undiagnosed cases, the fatality rate is likely lower than the death count divided by the confirmed case count.

## Plot types
The following Python scripts are provided in this repository:

### plot_conus_map.py
Plot a map of the Continental United States (CONUS) of COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases.

### plot_us_chart.py
Plot a time series of United States COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases. Flag to inclue/exclude repatriated cases (e.g., cruises) is included.

### plot_us_table.py
Plot a table of United States COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases. Flag to inclue/exclude repatriated cases (e.g., cruises) is included.

### plot_world_chart.py
Plot a time series of global COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases. Flag to inclue/exclude Mainland China is included.

### plot_world_table.py
Plot a table of global COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases. Flag to inclue/exclude Mainland China is included.
