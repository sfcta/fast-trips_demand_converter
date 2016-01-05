

from tables import openFile, IsDescription, Filters
from collections import defaultdict
import time, random, sys, os
import pandas as pd

from config import *
from util_functions import *
from person import Person


random.seed("rbtz")

infile = openFile(FILE_INPUT_ABM_DEMAND, mode="r")
rownum = 1
start       = time.time()

outfilename = os.path.join(OUTPUT_DIR, FILE_OUT_TRIP)
outfile = open(outfilename, mode="w")
outfile.write("person_id,o_taz,d_taz,mode,purpose,departure_time,arrival_time,time_target,vot,PNR_ids\n")

tempfilename = os.path.join(OUTPUT_DIR, FILE_TEMP)
temp_file = open(tempfilename, mode="w")
temp_file.write("hh_id,hh_vehicles,hh_income,hh_size,hh_workers,hh_presch,hh_elders,")
temp_file.write("person_id,age,gender,worker_status,work_athome,multiple_jobs,transit_pass,disability\n")


# read the preferred departure & arrival time distributions
pref_dep_time_dist = readDistributionCDFs(FILE_DEFAULT_DEPTIME_CDF)
pref_arr_time_dist = readDistributionCDFs(FILE_DEFAULT_ARRTIME_CDF)
# keep track of the simulated version
sim_dep_time_dist  = defaultdict(int)
sim_arr_time_dist  = defaultdict(int)

person          = None

for row in infile.root.records:
    if rownum % 1000000 == 0: print "Read %10d rows" % rownum
    rownum += 1

    if person:
        if person._persid != row['persid']:
            # the previous person is done - write them out
            person.sortTrips()
            person.choosePreferredTimes(pref_dep_time_dist, pref_arr_time_dist)
            person.write(outfile, sim_arr_time_dist, sim_dep_time_dist)
            person.write_temp(temp_file)
            # initialize the new person, add the trip
            person = Person(row)
        else:
            # add the trip
            person.addTrip(row)
    else:
        # initialize the new person, add the trip
        person = Person(row)
    
    
infile.close()
print "Read %s in %5.2f mins" % (FILE_INPUT_ABM_DEMAND, (time.time() - start)/60.0)

outfile.close()
temp_file.close()

hfilename = os.path.join(OUTPUT_DIR, FILE_OUT_HH)
pfilename = os.path.join(OUTPUT_DIR, FILE_OUT_PERSON)
hh_cols = ['hh_id', 'hh_vehicles', 'hh_income', 'hh_size', 'hh_workers', 'hh_presch', 'hh_elders']
per_cols = ['person_id', 'hh_id', 'age', 'gender', 'worker_status', 'work_athome', 'multiple_jobs', 'transit_pass', 'disability']
all_persons = pd.read_csv(tempfilename, usecols=per_cols)
all_hh = pd.read_csv(tempfilename, usecols=hh_cols)
all_hh = all_hh.drop_duplicates(subset='hh_id')
all_persons.to_csv(pfilename, index=False)
 
all_persons['hh_grdsch'] =  0
all_persons.loc[(all_persons.age >= 5) & (all_persons.age <= 15), 'hh_grdsch'] =  1
all_persons['hh_hghsch'] =  0
all_persons.loc[(all_persons.age >= 16) & (all_persons.age <= 17), 'hh_hghsch'] =  1
outhh_df = pd.DataFrame(all_persons.groupby(['hh_id'])[['hh_grdsch','hh_hghsch']].sum()).reset_index()
outhh_df = all_hh.merge(outhh_df, how='left', on='hh_id')
outhh_df.to_csv(hfilename, index=False)
os.remove(tempfilename)

print "Finished conversion in %5.2f mins" % ((time.time() - start)/60.0)

# # write the simulated preferred departure time
# outfile = open("Simulated_Preferred_Time.dat", mode="w")
# outfile.write("timebucket,pref_dep,pref_arr\n")
# for timebucket in range(3*60, (24+3)*60, 5):
#     outfile.write("%d,%d,%d\n" % (timebucket, sim_dep_time_dist[timebucket % (24*60)],sim_arr_time_dist[timebucket % (24*60)]))
# outfile.close()
