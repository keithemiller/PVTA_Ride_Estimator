# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 19:28:13 2016

@author: Keith E. Miller <keithmiller@umass.edu>


HackPVTA
"""

import pandas as pd
import numpy as np
from datetime import datetime
from urllib2 import urlopen, Request, URLError

class DM(object):
    """
    This class is for an object that will modify and store the data set.
    """

    ## Development Switches
    # Switch to True for Debug print statements
    DEBUG = True    
    
    ## Attributes
    # Name of the PVTA csv data file that will be loaded into the dataframe
    bus_filenames = ["April2015.csv", "March2015.csv"]
    bus_names = ["Vehicle_ID","Time","Latitude","Longitude"]    
    
    ## Data
    # The Pandas Dataframe object 
    df = None
    
    def __init__(self):
        """
        This function is called when you initialize the object.
        Example: data_object = data_mod()
        """
        if self.DEBUG: print "Object Created"

    def load_bus(self):
        """
        Loads the Bus data from the csv files
        """
        for f in self.bus_filenames:
            if self.df is None:
                self.df = pd.read_csv(f,
                                      low_memory=False,
                                      index_col=False,
                                      usecols=[0,1,2,3],
                                      names=self.bus_names)
            else:
                self.df = self.df.append(pd.read_csv(f,
                                                     low_memory=False,
                                                     index_col=False,
                                                     usecols=[0,1,2,3],
                                                     names=self.bus_names))
        self.df.Time = pd.to_datetime(self.df.Time)
        print self.df.Time        
        
    def load_weather(self):
        """
        Loads the weather from the weather csv files
        """
        pass
    
    def _get_semester(self, date_and_time):
        """
        Determines the semester of the date_and_time
        """
        
        return "spring"
    
    def query(self, weather=None, date_and_time=datetime.now()):
        """
        Gets the average data for the query and returns it
        """
        if weather is None:
            weather = self.get_weather()
        
        
        weekday = date_and_time.weekday()
        semester = self._get_semester(date_and_time)
        print "Weekday:", weekday
        print "Semester:", semester
            
    def get_weather(self):
        """
        Function will access the wunderground API to get the current weather
        conditions in the Amherst Area
        """
        
        # Key: 77ab162ff987e951
        # Example API call http://api.wunderground.com/api/Your_Key/conditions/q/CA/San_Francisco.json
        request = Request("http://api.wunderground.com/api/77ab162ff987e951/" \
        "conditions/q/CA/San_Francisco.json")        
        response = urlopen(request)        
        print response.read()
        json = response.read()
    
"""
Equivalent to Java's Main... This is what runs when we 
"""
if __name__=='__main__':
    print "Starting Up"
    dm = DM()
    dm.load_bus()
    dm.query()
    print "Done"