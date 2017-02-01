

# INPUT_TYPE = "CHAMP"
INPUT_TYPE = "CHTS"

if INPUT_TYPE=='CHAMP':
    ##### CHAMP

    FILE_INPUT_ABM_DEMAND = r"C:\Projects\SHRP2_FastTrips\FT_Demand\Validation\inputs\TRIPMC.H51"
    OUTPUT_DIR = r"C:\Projects\SHRP2_FastTrips\FT_Demand\Conversion"
    
    FILE_DEFAULT_DEPTIME_CDF = "PreferredDepartureTime.dat"
    FILE_DEFAULT_ARRTIME_CDF = "PreferredArrivalTime.dat"
    
    FILE_OUT_HH = "household.txt"
    FILE_OUT_PERSON = "person.txt"
    FILE_OUT_TRIP = "trip_list.txt"
    FILE_TEMP = "temp_ft.csv"
    
    PURPOSE_NUM_TO_STR      = {1:"Work",    2:"GradeSchool", 3:"HighSchool",
                               4:"College", 5:"Other",       6:"WorkBased" }
    PURPOSE_STR_TO_NUM      = dict((v,k) for k,v in PURPOSE_NUM_TO_STR.iteritems())
    TIMEPERIODS_NUM_TO_STR  = {1:"EA", 2:"AM", 3:"MD", 4:"PM", 5:"EV" }
    
    VISITOR_DEMAND_FLAG = True
    VISITOR_DEMAND_DIR = r"C:\Projects\SHRP2_FastTrips\FT_Demand\Validation\inputs\visitor"

elif INPUT_TYPE=='CHTS':
    ##### CHTS
    
    INPUT_DIR = r"Q:\Data\Surveys\HouseholdSurveys\CHTS2012\Processing\_2c_adjust_weights"
    INFILE_HH = "sfcta_chts_hrecx_rewt.dat"
    INFILE_PERSON = "sfcta_chts_precx_rewt.dat"
    INFILE_TOUR = "sfcta_chts_tourx_rewt.dat"
    INFILE_TRIP = "sfcta_chts_tripx_rewt.dat"
    
    OUTPUT_DIR = r"Q:\Model Development\SHRP2-fasttrips\Task3\chts_demand_conversion\version_0.3"
    FILE_OUT_HH = "household.txt"
    FILE_OUT_PERSON = "person.txt"
    FILE_OUT_TRIP = "trip_list.txt"
    
    GPS_TRIPS = True
    if GPS_TRIPS:
        OUTPUT_DIR = r"Q:\Model Development\SHRP2-fasttrips\Task3\chts_demand_conversion\version_0.4"
        GPS_TRIP_FILE = r"Q:\Data\Surveys\HouseholdSurveys\CHTS2012\Data\W1_CHTS_GPS_Final_Data_Deliverable_Wearable\CHTS_FToutput_wStopsRoutesTAZ.csv"
        
    
