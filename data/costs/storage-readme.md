# Historical price of computer memory and storage - Data package

This data package contains the data that powers the chart ["Historical price of computer memory and storage"](https://ourworldindata.org/grapher/historical-cost-of-computer-memory-and-storage?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website.

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For normal countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The remaining columns are the data columns, each of which is a time series. If the CSV data is downloaded using the "full data" option, then each column corresponds to one time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data columns are transformed depending on the chart type and thus the association with the time series might not be as straightforward.

## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

### How we process data at Our World In Data
All data and visualizations on Our World in Data rely on data sourced from one or several original data providers. Preparing this original data involves several processing steps. Depending on the data, this can include standardizing country names and world region definitions, converting units, calculating derived indicators such as per capita measures, as well as adding or adapting metadata such as the name or the description given to an indicator.
[Read about our data pipeline](https://docs.owid.io/projects/etl/)

## Detailed information about each time series


## Memory
This data is expressed in US dollars per terabyte (TB), adjusted for inflation.
Last updated: May 13, 2024  
Next update: May 2025  
Date range: 1957–2023  
Unit: constant 2020 US$ per terabyte  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data

#### Full citation
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data. “Memory” [dataset]. John C. McCallum, “Price and Performance Changes of Computer Technology with Time”; U.S. Bureau of Labor Statistics, “US consumer prices” [original data].
Source: John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World In Data

### What you should know about this data

### Sources

#### John C. McCallum – Price and Performance Changes of Computer Technology with Time
Retrieved on: 2024-05-13  
Retrieved from: https://jcmit.net/memoryprice.htm  

#### U.S. Bureau of Labor Statistics – US consumer prices
Retrieved on: 2024-05-16  
Retrieved from: https://www.bls.gov/data/tools.htm  


## Flash
This data is expressed in US dollars per terabyte (TB), adjusted for inflation.
Last updated: May 13, 2024  
Next update: May 2025  
Date range: 2003–2017  
Unit: constant 2020 US$ per terabyte  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data

#### Full citation
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data. “Flash” [dataset]. John C. McCallum, “Price and Performance Changes of Computer Technology with Time”; U.S. Bureau of Labor Statistics, “US consumer prices” [original data].
Source: John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World In Data

### What you should know about this data

### How is this data described by its producer - John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024)?
Flash memory provides a solid state alternative to disk drives, although at a greater cost per megabyte. In general, these are the lowest priced USB flash memory devices I could find. I have stopped recording separate flash prices, since SSDs are now the best source of flash memory prices.

### Sources

#### John C. McCallum – Price and Performance Changes of Computer Technology with Time
Retrieved on: 2024-05-13  
Retrieved from: https://jcmit.net/memoryprice.htm  

#### U.S. Bureau of Labor Statistics – US consumer prices
Retrieved on: 2024-05-16  
Retrieved from: https://www.bls.gov/data/tools.htm  


## Disk
This data is expressed in US dollars per terabyte (TB), adjusted for inflation.
Last updated: May 13, 2024  
Next update: May 2025  
Date range: 1956–2023  
Unit: constant 2020 US$ per terabyte  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data

#### Full citation
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data. “Disk” [dataset]. John C. McCallum, “Price and Performance Changes of Computer Technology with Time”; U.S. Bureau of Labor Statistics, “US consumer prices” [original data].
Source: John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World In Data

### What you should know about this data

### How is this data described by its producer - John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024)?
In general, these are the lowest priced disk drives for which I found prices at the time. The floppy drives are not the lowest price per capacity. Floppies are included because they set a low unit price, making disk drives accessible to the masses.

### Sources

#### John C. McCallum – Price and Performance Changes of Computer Technology with Time
Retrieved on: 2024-05-13  
Retrieved from: https://jcmit.net/memoryprice.htm  

#### U.S. Bureau of Labor Statistics – US consumer prices
Retrieved on: 2024-05-16  
Retrieved from: https://www.bls.gov/data/tools.htm  


## Solid state
This data is expressed in US dollars per terabyte (TB), adjusted for inflation.
Last updated: May 13, 2024  
Next update: May 2025  
Date range: 2013–2023  
Unit: constant 2020 US$ per terabyte  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data

#### Full citation
John C. McCallum (2023); U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World in Data. “Solid state” [dataset]. John C. McCallum, “Price and Performance Changes of Computer Technology with Time”; U.S. Bureau of Labor Statistics, “US consumer prices” [original data].
Source: John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024) – with minor processing by Our World In Data

### What you should know about this data

### How is this data described by its producer - John C. McCallum (2023), U.S. Bureau of Labor Statistics (2024)?
Flash memory provides a solid state alternative to disk drives, although at a greater cost per megabyte. In general, these are the lowest priced USB flash memory devices I could find. I have stopped recording separate flash prices, since SSDs are now the best source of flash memory prices.

### Sources

#### John C. McCallum – Price and Performance Changes of Computer Technology with Time
Retrieved on: 2024-05-13  
Retrieved from: https://jcmit.net/memoryprice.htm  

#### U.S. Bureau of Labor Statistics – US consumer prices
Retrieved on: 2024-05-16  
Retrieved from: https://www.bls.gov/data/tools.htm  


    