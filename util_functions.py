import random

def readDistributionCDFs(filename):
    """
    Distribution files are of the format:
    timeperiod, startmin, CDF
    
    Returns a dictionary: timeperiod -> [ (startmin, CDF) ]
    """
    distribution = {}
    distrib_file = open(filename, mode="r")
    for line in distrib_file:
        if line[0] in ['*',"#",";"]: continue # comment
        
        fields = line.split(",")
        timeperiod = fields[0]
        if timeperiod not in distribution:
            distribution[timeperiod] = []
        
        distribution[timeperiod].append((int(fields[1]), float(fields[2])))
    distrib_file.close()
    
    return distribution

def chooseTimeFromDistribution(distribution):
    """
    Given a distribution, which is a CDF defined by a list of [ (startmin1, CDF1), (startmin2, CDF2), ...]
    chooses a time (an integer, minutes since the start of the day) and returns it.
        
    Return range is based on the distribution.
    """
        
    r = random.random() # in [0.0, 1.0)
    prev_cdf = 0.0
    
    for idx in range(len(distribution)):

        if prev_cdf < r < distribution[idx][1]:
            # we're done - pick a time within the 5 min window
            return int(distribution[idx][0] + (r-prev_cdf)*(5.0)/(distribution[idx][1]-prev_cdf))
                
        prev_cdf = distribution[idx][1]

    raise Exception("chooseTimeFromDistribution: should never get here")

def getIntTrips(scaling_factor):
    """
    Given a float number of trips, rounds up or down based on the probability corresponding to the fractional part.
        
    For example: if 3.2 is passed, this will return 3 with probability 0.8 and 4 with probability 0.2
    """ 
    
    r = random.random() # in [0.0, 1.0)
    multiplier = int(scaling_factor)
    prob_scaling_factor = scaling_factor - multiplier
    if r < prob_scaling_factor:
        return multiplier + 1
    else:
        return multiplier

def convertTripTime(triptime, div=60):
    if int(triptime) > 0:
        hour = int(triptime/div)
        minute = triptime % div
        return '%02d:%02d:00' %(hour,minute)
    else:
        return ''

def calculateVOT(df_row):
    '''Based on SFCTA RPM-9 Report, p39:
        - non-work value of time = 2/3 work value of time,
        - Impose a minimum of $1/hour and a maximum of $50/hour,
        - Impose a maximum of $5/hour for workers younger than 18 years old.
    '''
    if int(df_row['age']) <= 18 and df_row['worker_status'] != 'unemployed':
        vot = 5
    if df_row['hh_income']<=0 or df_row['worker_status'] == 'unemployed':
        vot = 1
    elif int(df_row['hh_workers'])<=0:
        vot_w = float(df_row['hh_income'])/(52*40)
        vot = min(50,vot_w) if df_row['purpose']=='work' else min(50,0.67*vot_w)
    else:
        vot_w = (float(df_row['hh_income'])/int(df_row['hh_workers']))/(52*40)
        vot = min(50,vot_w) if df_row['purpose']=='work' else min(50,0.67*vot_w)
    
    return round(vot,2)
        
        
        
        
        
    