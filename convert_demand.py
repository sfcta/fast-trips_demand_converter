

from tables import openFile, IsDescription, Filters
from collections import defaultdict
import time, random, sys, os
import pandas as pd
import numpy as np
from tables import openFile

from config import *
from util_functions import *
from person import Person


random.seed("rbtz")
start       = time.time()

hfilename = os.path.join(OUTPUT_DIR, FILE_OUT_HH)
pfilename = os.path.join(OUTPUT_DIR, FILE_OUT_PERSON)
outfilename = os.path.join(OUTPUT_DIR, FILE_OUT_TRIP)

if INPUT_TYPE=="CHAMP":

    infile = openFile(FILE_INPUT_ABM_DEMAND, mode="r")
    rownum = 1
    
    outfile = open(outfilename, mode="w")
    outfile.write("person_id,person_trip_id,person_tour_id,o_taz,d_taz,mode,purpose,departure_time,arrival_time,time_target,vot,PNR_ids\n")
    
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
    temp_file.close()
    
    print "Reading visitor demand"
    # visitor demand
    if VISITOR_DEMAND_FLAG:
        visitor_trip_id = 0
        for idx, tp in TIMEPERIODS_NUM_TO_STR.iteritems():
            visit_file_name = os.path.join(VISITOR_DEMAND_DIR, tp.lower()+"VISIT.h5")
            visit_file = openFile(visit_file_name, "r")
            visitors = visit_file.get_node("/", "2") # this is the matrix with WLRT trips in it
            org_zones = visitors.shape[0]
            des_zones = visitors.shape[1]
    #         print sum(sum(visitors))
            for i in range(org_zones):
                for j in range(des_zones):
                    if visitors[i][j] > 0:
                        num_trips = getIntTrips(visitors[i][j])
                        for t in range(num_trips):
                            person_id = 0
                            visitor_trip_id += 1
                            otaz = i+1
                            dtaz = j+1
                            mode = 'walk-transit-walk'
                            purpose = 'visitor'
                            dep_time = chooseTimeFromDistribution(pref_dep_time_dist[tp])
                            arr_time = -1
                            time_target = 'departure'
                             
                            # person_id,person_trip_id,person_tour_id,o_taz,d_taz,mode,purpose,departure_time,arrival_time,time_target,vot,PNR_ids
                            outfile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.2f,%s\n" % 
                                          (person_id, visitor_trip_id, '', otaz, dtaz, mode, purpose, 
                                           convertTripTime(dep_time), convertTripTime(arr_time),
                                           time_target, -1,''))
            visit_file.close()
                        
    outfile.close()
    
    print "Creating household and person files"
    # household and person files
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


elif INPUT_TYPE=="CHTS":
    # read in survey files
    hh_df = pd.read_csv(os.path.join(INPUT_DIR, INFILE_HH), sep=' ')
    person_df = pd.read_csv(os.path.join(INPUT_DIR, INFILE_PERSON), sep=' ')
    
    hh_df = hh_df.rename(columns={'hhno':'hh_id','hhvehs':'hh_vehicles','hhincome':'hh_income','hhsize':'hh_size','hhwkrs':'hh_workers',
                                  'hhcu5':'hh_presch','hh515':'hh_grdsch','hhhsc':'hh_hghsch'})
    person_df = person_df.rename(columns={'hhno':'hh_id','pno':'person_id','pagey':'age'})
    
    ### prepare and write out hh file
    person_df['hh_elders'] = 0
    person_df.loc[person_df['age'] >= 65, 'hh_elders'] =  1
    agg_df = pd.DataFrame(person_df.groupby(['hh_id'])[['hh_elders']].sum()).reset_index()
    hh_df = hh_df.merge(agg_df, how='left', on='hh_id')
    
#     hh_df['hh_income'] =  hh_df['hh_income'].astype(int)
#     hh_df.loc[hh_df['hh_income']<0,'hh_income'] = np.nan
    
    hh_cols = ['hh_id', 'hh_vehicles', 'hh_income', 'hh_size', 'hh_workers', 'hh_presch', 'hh_grdsch', 'hh_hghsch', 'hh_elders']
    hh_df.to_csv(hfilename, columns=hh_cols, index=False)
    
    ### prepare and write out person file
    person_df['gender'] = ''
    person_df.loc[person_df['pgend']==1 ,'gender'] = 'male'
    person_df.loc[person_df['pgend']==2 ,'gender'] = 'female'
    
    person_df['worker_status'] = 'unemployed'
    person_df.loc[person_df['pwtyp']==1 ,'worker_status'] = 'full-time'
    person_df.loc[person_df['pwtyp']==2 ,'worker_status'] = 'part-time'
    
    person_df['work_athome'] = 'False'
    person_df['multiple_jobs'] = 'False'
    person_df['transit_pass'] = 'False'
    person_df['disability'] = 'none'
    
    person_df['person_id'] = person_df['hh_id'].astype(str) + '_' + person_df['person_id'].astype(str)
    per_cols = ['person_id', 'hh_id', 'age', 'gender', 'worker_status', 'work_athome', 'multiple_jobs', 'transit_pass', 'disability']
    person_df.to_csv(pfilename, columns=per_cols, index=False)    
    
    if not GPS_TRIPS:
        tour_df = pd.read_csv(os.path.join(INPUT_DIR, INFILE_TOUR), sep=' ')
        trip_df = pd.read_csv(os.path.join(INPUT_DIR, INFILE_TRIP), sep=' ')
    
        ### prepare and write out trip file
        trip_df = trip_df.loc[trip_df['mode'].isin(range(6,16)),] # keep only transit trips
        trip_df = trip_df.loc[(trip_df['otaz']>0) & (trip_df['dtaz']>0),]
        trip_df = trip_df.merge(tour_df[['hhno','pno','tour','parent']], how='left', on=['hhno','pno','tour'])
        trip_df = trip_df.rename(columns={'hhno':'hh_id','pno':'person_id','otaz':'o_taz','dtaz':'d_taz','tour':'person_tour_id','mode':'survey_mode'})
        trip_df['person_id'] = trip_df['hh_id'].astype(str) + '_' + trip_df['person_id'].astype(str)
        
        # 6=walk local 7=walk lrt 8=walk prem 9=walk ferry 10=walk bart
        # 11=drive local 12=drive lrt 13=drive prem 14=drive ferry 15=drive bart
        trip_df['mode'] = 'walk-transit-walk'
        trip_df.loc[(trip_df['survey_mode'].isin(range(11,16))) & (trip_df['half']==1), 'mode'] = 'PNR-transit-walk'
        trip_df.loc[(trip_df['survey_mode'].isin(range(11,16))) & (trip_df['half']==2), 'mode'] = 'walk-transit-PNR'
        
        trip_df = trip_df.merge(hh_df[['hh_id','hh_income','hh_workers']], how='left', on=['hh_id'])
        trip_df = trip_df.merge(person_df[['person_id','pptyp','age','worker_status']], how='left', on=['person_id'])
        trip_df['purpose'] = 'other'
        trip_df.loc[trip_df['dpurp']==1, 'purpose'] = 'work'
        trip_df.loc[(trip_df['dpurp']==2) & (trip_df['pptyp']==7), 'purpose'] = 'grade_school'
        trip_df.loc[(trip_df['dpurp']==2) & (trip_df['pptyp']==6), 'purpose'] = 'high_school'
        trip_df.loc[(trip_df['dpurp']==2) & (trip_df['pptyp']==5), 'purpose'] = 'college'
        trip_df.loc[trip_df['parent']>0, 'purpose'] = 'work_based'
        
        trip_df['vot'] = trip_df.apply(calculateVOT,axis=1)
        trip_df['departure_time'] = trip_df['deptm'].apply(convertTripTime, args=(100,))
        trip_df['arrival_time'] = trip_df['arrtm'].apply(convertTripTime, args=(100,))
        trip_df['time_target'] = 'departure'
        trip_df.loc[trip_df['half']==1, 'time_target'] = 'arrival'
        trip_df['person_trip_id'] = trip_df['person_tour_id'].astype(str) + '_' + trip_df['half'].astype(str) + '_' + trip_df['tseg'].astype(str)
    else:
        transit_legs = pd.read_csv(GPS_TRIP_FILE)
        trip_df = transit_legs.drop_duplicates(['person_id','trip_list_id_num'])[['person_id','trip_list_id_num','A_id','new_A_time','mode']]
        trip_count = trip_df.groupby('person_id').count().reset_index()
        trip_df['person_trip_id'] = [item for l in trip_count['trip_list_id_num'].apply(range).tolist() for item in l]
        trip_df['person_trip_id'] = trip_df['person_trip_id'] + 1
#         trip_df['person_trip_id'] = trip_df['person_id'].astype(str) + '_' + trip_df['person_trip_id'].astype(str)
        
        trip_df = trip_df.rename(columns={'mode':'mode1'})
        temp_df = transit_legs.drop_duplicates(['person_id','trip_list_id_num'], keep='last')[['person_id','trip_list_id_num','B_id','new_B_time','mode']]
        trip_df = trip_df.merge(temp_df, on=['person_id','trip_list_id_num'], how='left')
        trip_df = trip_df.rename(columns={'A_id':'o_taz','B_id':'d_taz','new_A_time':'departure_time','new_B_time':'arrival_time','mode':'mode2'})
        
        trip_df['arr_hour'] = trip_df['arrival_time'].apply(lambda x: int(x.split(":")[0]))
        trip_df['dep_hour'] = trip_df['departure_time'].apply(lambda x: int(x.split(":")[0]))
        trip_df['time_target'] = 'departure'
        trip_df.loc[trip_df['arr_hour']<=12, 'time_target'] = 'arrival'
        
        trip_df['hh_id'] = trip_df['person_id'].apply(lambda x: int(x.split("_")[0]))
        trip_df = trip_df.merge(hh_df[['hh_id','hh_income','hh_workers']], how='left', on=['hh_id'])
        trip_df = trip_df.merge(person_df[['person_id','pptyp','age','worker_status']], how='left', on=['person_id'])
        trip_df.loc[pd.isnull(trip_df['age']), 'age'] = -1
        trip_df.loc[pd.isnull(trip_df['hh_workers']), 'hh_workers'] = -1
        trip_df['tp'] = ''
        trip_df.loc[(trip_df['dep_hour']>=6) & (trip_df['dep_hour']<=9), 'tp'] = 'AM'
        
        trip_df['purpose'] = 'other' # default
        trip_df.loc[(trip_df['tp']=='AM') & (((trip_df['pptyp']==1)) | (trip_df['pptyp']==2)), 'purpose'] = 'work'
        trip_df.loc[(trip_df['tp']=='AM') & (trip_df['pptyp']==7), 'purpose'] = 'grade_school'
        trip_df.loc[(trip_df['tp']=='AM') & (trip_df['pptyp']==6), 'purpose'] = 'high_school'
        trip_df.loc[(trip_df['tp']=='AM') & (trip_df['pptyp']==5), 'purpose'] = 'college'
        
        trip_df['vot'] = trip_df.apply(calculateVOT,axis=1)
        trip_df['mode'] = 'walk-transit-walk'
        trip_df.loc[trip_df['mode1'].isin(['PNR_access','KNR_access']), 'mode'] = 'PNR-transit-walk'
        trip_df.loc[trip_df['mode2'].isin(['PNR_egress','KNR_egress']), 'mode'] = 'walk-transit-PNR'
        
        trip_df = trip_df.loc[(pd.notnull(trip_df['o_taz'])) & (pd.notnull(trip_df['d_taz'])),]
        trip_df[['o_taz','d_taz']] = trip_df[['o_taz','d_taz']].astype(int)
        
        
    trip_df = trip_df.loc[trip_df['person_id'].isin(person_df['person_id']),]
    trip_df = trip_df.sort_values(['person_id','person_trip_id'])
    trip_cols = ['person_id', 'person_trip_id', 'person_tour_id', 'o_taz', 'd_taz', 'mode', 'purpose', 'departure_time', 'arrival_time', 'time_target', 'vot']
    trip_df.to_csv(outfilename, columns=trip_cols, index=False)
    

print "Finished conversion in %5.2f mins" % ((time.time() - start)/60.0)


