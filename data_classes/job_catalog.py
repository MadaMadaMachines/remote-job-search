#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Human_001B
#
# Created:     06/02/2023
# Copyright:   (c) Human_001B 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# using pandas would make these kind of moot

from job_details import (
                    job_details,
                    G_JTITLE,
                    G_JSALARYF,
                    G_JSALARYR,
                    G_JDESCRIP,
                    G_JSKILLR,
                    G_JSKILLF,
                    G_JLINK,
                    G_JREQSKILL,
                    G_JBONUSSKILL,
                    G_JPOSTDATE,
                    G_JLASTPOSTDATE,
                    G_CNAME,
                    G_CTITLE,
                    G_CEMAIL,
                    )

class job_catalog():
    def __init__(self):
        self.results_dict = {}  # where key is url and value is job_details object

    def add_new_result(self, jdetail_obj : job_details = None):
        if job_details != None:
            # could do more sanity chks
            if job_details.job_link in self.results_dict.keys():
                # we hit a link we already scraped
                #  is there new data or has the job stopped accepting apps or no longer listed?
                pass
            else:
                self.results_dict[job_details.job_link] = job_details
        # else nothing to process

    def to_dataframe(self):
        pass
        # use pandas and conver the list of dictionaries into a dataframe

    ## no need for tocsv as that's baked into pandas.dataframes
