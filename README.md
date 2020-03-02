# COVID-19
A collection of scripts to visualize real-time COVID-19 data from John Hopkins CSSE.

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
This repository contains scripts that visualize real-time COVID-19 data from John Hopkins SSE:
https://github.com/CSSEGISandData/COVID-19

Data from this source are limited to the same constraints and terms of use as posted on the CSSE GIS and Data GitHub page.

### plot_conus_map.py
Plot a map of the Continental US of COVID-19 cases, including confirmed cases, deaths, recoveries, ongoing cases, and daily new cases.
