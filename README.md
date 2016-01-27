# SF-CHAMP to Fast-Trips Demand Data Converter

Converts disaggregate SF-CHAMP Activity-Based Travel Model demand to [Fast-Trips](https://github.com/MetropolitanTransportationCommission/fast-trips) input demand using time of day distributions from observed transit boardings and alightings.

`python convert_demand.py`

Reads:     `TRIPMC.H51` (SF-CHAMP trip file in HDF5 format)  
Writes:    Input demand to [Fast-Trips](https://github.com/MetropolitanTransportationCommission/fast-trips) in [Dyno-Demand](https://github.com/osplanning-data-standards/dyno-demand) format:  
 - [`household.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/household.md)
 - [`person.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/person.md)
 - [`trip_list.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/trip_list.md) 

Configuration: [`config.py`](https://github.com/sfcta/fast-trips_demand_converter/blob/master/config.py)

Default time-of-day CDFs derived from 2012 [MUNI](http://www.sfmta.com) [APC](http://www.transitwiki.org/TransitWiki/index.php?title=Automated_Passenger_Counter) data.:  
 - [`PreferredDepartureTime.dat`](https://github.com/sfcta/fast-trips_demand_converter/blob/master/PreferredDepartureTime.dat)  
 - [`PreferredArrivalTime.dat`](https://github.com/sfcta/fast-trips_demand_converter/blob/master/PreferredArrivalTime.dat)

This is based on a script originally written by [Lisa Zorn](https://github.com/lmz) and [Alireza Khani](https://github.com/akhani) in 2012:
`Q:\Model Development\FastTrips\Demand.CHAMP\ft_CHAMPdemandGenerator.py`

