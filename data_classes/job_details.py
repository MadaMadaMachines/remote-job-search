#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Human_001B
#
# Created:     14/11/2022
# Copyright:   (c) Human_001B 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# there any use for this vs directly going to pandas df using the same column titles?


## column headers
G_JTITLE      = "Job_Title"
G_JSALARYF    = "Job_Salary_Formatted"
G_JSALARYR    = "Job_Salary_Raw"
G_JDESCRIP    = "Job_Description"
G_JSKILLR     = "Job_Skills_Raw"
G_JSKILLF     = "Job_Skills_Formattted"
G_JLINK       = "Job_Source_URL"
G_JREQSKILL   = "Job_Required_Skills"
G_JBONUSSKILL = "Job_Bonus_Skills"
G_JPOSTDATE   = "Job_Post_Date"
G_JLASTPOSTDATE = "Job_RePost_Date"
G_CNAME  = "Contact_Name"
G_CTITLE = "Contact_Title"
G_CEMAIL = "Contact_Email"


class job_details():
    def __init__(self):
        self.job_title = ""
        self.job_salary_formatted = ""
        self.job_salary_raw = ""
        self.job_descrip_raw = ""
        self.job_skills_raw = ""
        self.job_skills_formatted = []
        self.job_link = ""
        self.base_req_skills = []
        self.bonus_pt_skills = []
        self.original_listing_date = ""
        self.last_updated_date = ""
        self.contact_name = ""
        self.contact_email = ""
        self.contact_title = ""

    def to_dict(self):
        attrs_dict = {}
        attrs_dict = {
                    G_JTITLE: self.job_title,
                    G_JSALARYF: self.job_salary_formatted,
                    G_JSALARYR: self.job_salary_raw,
                    G_JDESCRIP: self.job_descrip_raw,
                    G_JSKILLR: self.job_skills_raw,
                    G_JSKILLF: self.job_skills_formatted,
                    G_JLINK: self.job_link,
                    G_JREQSKILL: self.base_req_skills,
                    G_JBONUSSKILL: self.bonus_pt_skills,
                    G_JPOSTDATE: self.original_listing_date,
                    G_JLASTPOSTDATE: self.last_updated_date,
                    G_CNAME: self.contact_name,
                    G_CTITLE: self.contact_title,
                    G_CEMAIL: self.contact_email
                    }
        return attrs_dict



