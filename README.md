# fast-trips_demand_converter
Converts ABM transit demand to fast-trips input demand.
Reads:     TRIPMC.H51 (SF-CHAMP trip file in HDF5 format)
Writes:    household.txt, person.txt, and trip_list.txt (input demand to fast-trips)

Default time-of-day CDFs (`PreferredDepartureTime.dat` and `PreferredArrivalTime.dat`) were derived from 2012 MUNI APC data.

This is based on the a script originally written by Lisa Zorn and Alireza Khani in 2012:
`Q:\Model Development\FastTrips\Demand.CHAMP\ft_CHAMPdemandGenerator.py`

