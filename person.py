from config import *
from util_functions import *

class Person(object):
    """
    Minimal class representing a set of person records
    """
    IDX_TOUR        = 0
    IDX_PURPOSE     = 1
    IDX_SEGDIR      = 2
    IDX_CURRSEG     = 3
    IDX_OTAZ        = 4
    IDX_DTAZ        = 5
    IDX_ODT         = 6
    IDX_TRIPMODE    = 7
    IDX_MVOT        = 8
    IDX_OVOT        = 9
    IDX_PREF_ARR    = 10
    IDX_PREF_DEP    = 11
    
    
    def __init__(self, row):
        """
        Row is a table row.  Initialize and call addTrip()
        """
        self._hhid   = row['hhid']
        self._persid = row['persid']

        hh_income = str(int(round(row['hhinc']*1000)))
        person_id = str(row['hhid']) + '_' + str(row['persid'])
        gender = 'male' if row['gender']==1 else 'female'
        multiple_jobs = 'True' if row['worksTwoJobs']==1 else 'False'
        self._persrec = [str(row['hhid']),str(row['autos']),hh_income,str(row['hhsize']),str(row['nfulltim']+row['nparttim']),str(row['nageund5']),str(row['nage65up']),
                         person_id,str(row['age']),gender,self.getWorkerStatus(row['employ']),'False', multiple_jobs, 'False', 'none']
        
        # the trips
        self._trips = []
        self.addTrip(row)

    def addTrip(self, row):
        """
        Add this trip to the person
        """
        assert(self._persid == row['persid'])
        self._trips.append( [row['tour'], row['purpose'], row['mSegDir'], row['mcurrseg'], 
                             row['mOtaz'], row['mDtaz'], row['mOdt'], row['mChosenmode'],
                             row['mVOT'], row['oVOT'] ])
    
    def sortTrips(self):
        """
        Trips are sorted by tour initially.
        Re-order to sort by trips (only matters with work-based tours)
        """
        # find index of row at for the last outbound work trip
        last_outbound_work_idx = -1
        # and the work-based trips
        first_workbased_trip_idx = -1
        last_workbased_trip_idx  = -1
        
        for idx in range(len(self._trips)):
            # work outbound
            if (self._trips[idx][Person.IDX_PURPOSE] == PURPOSE_STR_TO_NUM["Work"] and 
                self._trips[idx][Person.IDX_SEGDIR] == 1):
                last_outbound_work_idx = idx

            if self._trips[idx][Person.IDX_PURPOSE] == PURPOSE_STR_TO_NUM["WorkBased"]:
                # only set this once
                if first_workbased_trip_idx == -1:
                    first_workbased_trip_idx = idx
                last_workbased_trip_idx = idx
    
        # no work-based trips? nothing to do
        if first_workbased_trip_idx == -1:
            return
                
        # we need to have work trips for work-based trips
        assert(last_outbound_work_idx >= 0)
        
        # workbased are after work
        # print last_outbound_work_idx, first_workbased_trip_idx, last_workbased_trip_idx
        assert(first_workbased_trip_idx > last_outbound_work_idx)
            
        # now re-order -- move the workbased to be after the last outbound work trip
        workbased_trips = []
        for idx in range(first_workbased_trip_idx, last_workbased_trip_idx+1):
            # pop it off
            workbased_trips.append(self._trips.pop(first_workbased_trip_idx))
            
        # print "workbased_trips=",workbased_trips
        while len(workbased_trips) > 0:
            self._trips.insert(last_outbound_work_idx+1, workbased_trips.pop())

        # debug
        # print self._trips
        
        # now verify that the trips have time periods in order
        for idx in range(len(self._trips)-1):
            if self._trips[idx][Person.IDX_ODT] > self._trips[idx+1][Person.IDX_ODT]:
                pass
                # print "Warning: person %d has sorted trips have non-sequential odts @ index %d: " % (self._persid, idx)
                # for trip in self._trips:
                #    print trip

    def choosePreferredTimes(self, pref_dep_time_dist, pref_arr_time_dist):
        """
        """
        for trip in self._trips:
                   
            # choose preferred arrival time
            timeperiod = TIMEPERIODS_NUM_TO_STR[trip[Person.IDX_ODT]]
            
            if trip[Person.IDX_SEGDIR] == 1:
                # outbound - set arrival time
                pref_arr = chooseTimeFromDistribution(pref_arr_time_dist[timeperiod])
                pref_arr = pref_arr % (24*60)
                pref_dep = -1
            else:
                # inbound - set departure time
                pref_dep = chooseTimeFromDistribution(pref_dep_time_dist[timeperiod])
                pref_dep = pref_dep % (24*60)
                pref_arr = -1
            
            trip.append(pref_arr)
            trip.append(pref_dep)
            
        # sort preferred times within a time period so they're sequential
        pref_times = []
        cur_timeperiod = None
        for trip_idx in range(len(self._trips)):
            trip = self._trips[trip_idx]
            
            # new time period
            if trip[Person.IDX_ODT] != cur_timeperiod:
                
                # sort the previous ones pref_times so they're sequential
                if len(pref_times)>0:
                    pref_times = sorted(pref_times)
                    pref_idx = 0
                    for tp_idx in range(trip_idx - len(pref_times), trip_idx):
                        if self._trips[tp_idx][Person.IDX_PREF_DEP] >= 0:
                            self._trips[tp_idx][Person.IDX_PREF_DEP] = pref_times[pref_idx]
                        else:
                            self._trips[tp_idx][Person.IDX_PREF_ARR] = pref_times[pref_idx]
                        pref_idx += 1
                
                # reset
                pref_times = []
            
            # add this pref time
            if self._trips[trip_idx][Person.IDX_PREF_DEP] >= 0:
                pref_times.append(self._trips[trip_idx][Person.IDX_PREF_DEP])
            else:
                pref_times.append(self._trips[trip_idx][Person.IDX_PREF_ARR])
            cur_timeperiod = trip[Person.IDX_ODT]
            
    def write(self, outfile, sim_arr_time_dist, sim_dep_time_dist):
        """
        Write the trips to the outfile, tab-delimited
        """
        for trip in self._trips:

            # transit only       
            if trip[Person.IDX_TRIPMODE] not in range(12,22): continue
            
            # record sim times for histogram output
            if trip[Person.IDX_PREF_ARR] >= 0:
                sim_arr_time_dist[trip[Person.IDX_PREF_ARR] - (trip[Person.IDX_PREF_ARR]%5)] += 1
            elif trip[Person.IDX_PREF_DEP] >= 0:
                sim_dep_time_dist[trip[Person.IDX_PREF_DEP] - (trip[Person.IDX_PREF_DEP]%5)] += 1 
            
            person_id = str(self._hhid) + '_' + str(self._persid)
            time_target = 'arrival' if trip[Person.IDX_SEGDIR] == 1 else 'departure' 
            vot = trip[Person.IDX_MVOT] if trip[Person.IDX_PURPOSE] in range(1,5) else trip[Person.IDX_OVOT]
            # person_id,person_trip_id,person_tour_id,o_taz,d_taz,mode,purpose,departure_time,arrival_time,time_target,vot,PNR_ids
            outfile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.2f,%s\n" % 
                          (person_id,trip[Person.IDX_CURRSEG],trip[Person.IDX_TOUR],
                           trip[Person.IDX_OTAZ], trip[Person.IDX_DTAZ],
                           self.getTripMode(trip[Person.IDX_TRIPMODE], trip[Person.IDX_SEGDIR]),
                           self.getTripPurpose(trip[Person.IDX_PURPOSE]),
                           convertTripTime(trip[Person.IDX_PREF_DEP]), convertTripTime(trip[Person.IDX_PREF_ARR]),
                           time_target, vot,''))
    
    def write_temp(self, outfile):
        outfile.write("%s\n" %(','.join(self._persrec)))
                           
    def getTripPurpose(self, purpcode):
        if purpcode==1: return 'work'
        elif purpcode in [2,3,4]: return 'school'
        elif purpcode==6: return 'work_based'
        else: return 'other'
    
    def getTripMode(self, modecode, segdir):
        
        if modecode < 17:
            return 'walk-transit-walk'
        else:
            if segdir == 1:
                access_mode = 'PNR'
                egress_mode = 'walk'
            else:
                access_mode = 'walk'
                egress_mode = 'PNR'
            return access_mode + '-transit-' + egress_mode 
        
#         submodes = ['local_bus', 'light_rail', 'premium', 'ferry', 'bart']
#         if modecode < 17:
#             transit_mode = submodes[modecode-12]
#             access_mode = 'walk'
#             egress_mode = 'walk'
#         else:
#             transit_mode = submodes[modecode-17]
#             if segdir == 1:
#                 access_mode = 'PNR'
#                 egress_mode = 'walk'
#             else:
#                 access_mode = 'walk'
#                 egress_mode = 'PNR'
#         return access_mode + '-' + transit_mode + '-' + egress_mode       
    
    def getWorkerStatus(self, empcode):
        empcode = int(empcode)
        if empcode in [1,3]: return 'full_time'
        elif empcode in [2,4]: return 'part_time'
        else: return 'unemployed'