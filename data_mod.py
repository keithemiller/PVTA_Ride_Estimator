# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 19:28:13 2016

@author: Keith E. Miller <keithmiller@umass.edu>

HackPVTA
********

This code combines PVTA Vehicle data with NOAA weather stored weather data
and Wunderground current weather conditions to provide an estimated time for
buses based off of day of the week, semester, and current set of weather data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from urllib2 import urlopen, Request, URLError
import json

class DM(object):
    """
    This class is for an object that will modify and store the data set.
    """

    ## Development Switches
    # Switch to True for Debug print statements
    DEBUG = True   
    TESTING = False
    
    ## Attributes
    # Name of the PVTA csv data file that will be loaded into the dataframe
    bus_filenames = {4:"April2015.csv", 3:"March2015.csv", 
                     2:"February2015.csv", 7:"July2015.csv",
                     1:"January2015.csv", 5:"May2015.csv",
                     6:"June2015.csv", 8:"August2015.csv",
                     9:"September2015.csv", 10:"October2015.csv",
                     11:"November2015.csv", 12:"December2015.csv"}
    bus_names = ["Vehicle_ID","Time","Trip","Passengers", "Stops", "Routes"]
    semester_dates = {"summer_end":(8,30),"fall_end":(12,28),
                      "winter_end":(1,19),"spring_end":(5,5)}    
    semester_ranges = {"summer":(5,8),"winter":(12,1),
                       "fall":(8,12),"spring":(1,5)}
    ## Data
    # The Pandas Dataframe object 
    df = None
    mod_df = None
    s1_df = None
    s2_df = None
    
    ## Output
    query_param  = {}
    output_dict = {}
    
    def __init__(self):
        """
        This function is called when you initialize the object.
        Example: data_object = data_mod()
        """
        if self.DEBUG: print "Object Created"
        print "DEBUG:", self.DEBUG
        print "TESTING:", self.TESTING        
        
        
    def load_bus(self, semester=None):
        """
        Loads the Bus data from the csv files of the months corresponding to
        the corresponding semesters.
        """
        if semester is None:
            for f in self.bus_filenames.values():
                if self.df is None:
                    self.df = pd.read_csv(f,
                                          low_memory=False,
                                          index_col=False,
                                          usecols=[0,1,11,14,18,20],
                                          names=self.bus_names)
                else:
                    self.df = self.df.append(pd.read_csv(f,
                                                         low_memory=False,
                                                         index_col=False,
                                                         usecols=[0,1,11,14,18,
                                                                  20],
                                                         names=self.bus_names))
        
        else:
            start, finish = self.semester_ranges[semester]
            for n in range(start, finish + 1):
                if self.df is None:
                    self.df = pd.read_csv(self.bus_filenames[n],
                                          low_memory=False,
                                          index_col=False,
                                          usecols=[0,1,11,14,18,20],
                                          names=self.bus_names)
                else:
                    self.df = self.df.append(pd.read_csv(self.bus_filenames[n],
                                                         low_memory=False,
                                                         index_col=False,
                                                         usecols=[0,1,11,14,18,
                                                                  20],
                                                         names=self.bus_names))

        ## Convert Time to a datetime datatype     
        self.df.Time = pd.to_datetime(self.df.Time)

        
    def load_weather(self):
        """
        Loads the weather from the weather csv files
        """
        self.w_df = pd.read_csv("682880.csv",
                                low_memory=False, 
                                usecols=[2,3,5,6,7])
    
    def _get_semester(self, date_and_time):
        """
        Determines the semester of the date_and_time
        """
        print date_and_time
        month = date_and_time.month
        day = date_and_time.day
        md = (month, day)
        semester = "spring"
        
        if ((self.semester_dates["fall_end"] <= md) or 
        (md <= self.semester_dates["winter_end"])):
            semester = "winter"
        elif ((self.semester_dates["spring_end"] <= md) and 
        (md <= self.semester_dates["summer_end"])):
            semester = "summer"
        elif ((self.semester_dates["summer_end"] <= md) and 
        (md <= self.semester_dates["fall_end"])):
            semester = "fall"
        else:
            semester = "spring"
        return semester
              
    
    def query(self, weather=None, date_and_time=datetime.now(),
              stop_a="Integrative Lea", stop_b="Fine Arts Cente", route=35):
        """
        Gets the average data for the query and returns it
        """
        if weather is None:
            #weather = self.get_weather()
            print "WEATHER TURNED OFF"
        if weather is None:
            if self.DEBUG: print "NO HOW ONE DO WEATHER?"
        weekday = date_and_time.weekday()
        if weekday >= 4:
            weekend = True
        else:
            weekend = False
        semester = self._get_semester(date_and_time)
        
        hour = date_and_time.hour
        if self.TESTING: hour = 8
            
        self.query_param["Weekday:"] = weekday
        self.query_param["Weekend:"] = weekend
        self.query_param["Semester:"] = semester
        self.query_param["Hour:"] = hour        
        
        if self.DEBUG: print self.query_param
        
        self.load_bus(semester=semester)
        
        self.filter_data(weekend, hour, stop_a, stop_b, route)
        
        print self.output_dict

        ret = (self.output_dict["Basic_Average"], 
        self.output_dict["Crowdedness"])
        
        print ret
        return ret
                    
            
    def get_weather(self):
        """
        Function will access the wunderground API to get the current weather
        conditions in the Amherst Area. Sets self.real_feel and self.weather.
        """
        
        # Key: 77ab162ff987e951
        # Example API call 
        # http://api.wunderground.com/api/Your_Key/    CONTINUED ON NEXT LINE
        # conditions/q/CA/San_Francisco.json
        request = Request("http://api.wunderground.com/api/77ab162ff987e951/" \
        "conditions/q/MA/Amherst.json")        
        try:
            response = urlopen(request)        
            json_weather = response.read()
            weather_dict = json.loads(json_weather)
            self.real_feel = weather_dict["current_observation"]["feelslike_f"]
            self.weather = weather_dict["current_observation"]["weather"]
        except URLError, e:
            print "CANNOT ACCESS WEATHER DATA", e
            return None

    def filter_data(self, weekend, hour, stop_a, stop_b, route):
        """
        The workhorse method of data_mod. This method performs all the
        operations on the dataframes to get the response for the query.
        """
        self.df["Weekend"] = self.df.Time.map(lambda x: x.weekday() >= 4)
        self.df["Hour"] = self.df.Time.map(lambda x: x.hour)

        self.mod_df = self.df.loc[self.df['Weekend'] == weekend]
        self.mod_df = self.mod_df.loc[((self.mod_df['Hour'] >= (hour - 1)) & \
        (self.mod_df['Hour'] <= (hour + 1)))]
        
        self.mod_df = self.mod_df.loc[self.mod_df['Routes'] == route]
        
        ## Stop 1 Data
        self.s1_df = self.mod_df.loc[self.mod_df['Stops'] == stop_a]
        self.s1_df.drop_duplicates(cols='Time', keep='last')        
        self.s1_df.sort_values(by='Time')
        self.s1_df.index = range(self.s1_df.shape[0])
        
        
        ## Stop 2 Data
        self.s2_df = self.mod_df.loc[self.mod_df['Stops'] == stop_b]
        self.s2_df.drop_duplicates(cols='Time', keep='last')        
        self.s2_df.sort_values(by='Time')
        self.s2_df.index = range(self.s2_df.shape[0])        
            
        self.load_weather()
        print self.w_df
        
        times = []
        adv_times = []
        crowds = []     
        
        for ii in range(0, self.s1_df.shape[0]):
            s1 = self.s1_df.loc[ii]
            s2 = self.s2_df.loc[(self.s2_df['Trip'] == s1.Trip) & \
            (self.s2_df['Vehicle_ID'] == s1.Vehicle_ID)]
            s2 = s2.sort_values(by='Time')
            s2.index = range(s2.shape[0])          
            try:
                tot = 0
                for z in range(s2.shape[0]):
                    tot += s2.loc[0].Passengers
                tot = float(tot) / s2.shape[0]
                times.append(((s2.loc[0].Time - s1.Time)).seconds / 60.0)
                crowds.append(tot)
            except:
                pass

        crowdedness = "Minimal"
        c_scalar = np.average(crowds) 
        print "Crowd_Scalar", c_scalar
        if c_scalar > 7: crowdedness = "Could be worse"
        if c_scalar > 14: crowdedness = "Cluster-F"
        
        self.output_dict["Basic_Average"] =  np.average(times)
        self.output_dict["Crowdedness"] = crowdedness
        self.output_dict["Advanced_Average"] = np.average(adv_times)
        

def new_datetime(dt):
    """
    *** DEPRECATED ***
    Function used to set all seconds and microseconds of a datetime object to
    zero. This was to be used to get rid of duplicates within the same minute
    previously, but was decided against to provide greater resolution.
    """
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
   
"""
Equivalent to Java's Main... This is what runs when we press the run button
"""
if __name__=='__main__':
    print "Starting Up"
    dm = DM()
    avg, crowd = dm.query()
    print "AVG:", avg
    print "CROWD:", crowd
    print "Done"