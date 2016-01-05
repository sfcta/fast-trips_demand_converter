

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