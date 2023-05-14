import pandas as pd
import requests
from math import ceil
from time import sleep, time

from bs4 import BeautifulSoup

# beautifulsoup version of indeed search, processes listing far faster than selenium

start_time = time()

indeed_base_search = "https://www.indeed.com/jobs?q=python&l=Remote&jt=fulltime&sort=date"
indeed_rem_py_44d = "http://www.indeed.com/jobs?q=python&l=Remote&sc=0bf%3Aexrec%28%29%2Ckf%3Aattr%28DSQF7%29%3B&sort=date&fromage=44"
headers = {"User-Agent": "Mozilla/5.0"}  # think this was added to help avoid bot detection, not sure if can be removed


response = requests.get(indeed_rem_py_44d, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
num_jobs = soup.find("div", class_="jobsearch-JobCountAndSortPane-jobCount").find("span").text.strip() # .jobsearch-JobCountAndSortPane-jobCount
nums_jobs_num = int( num_jobs.replace(" jobs", "").replace(",", "") )
num_res_pages = ceil(nums_jobs_num/10)
print ( str( num_res_pages  ) + "\n\n")

df_jobs = pd.DataFrame(columns=['title', 'company_name', 'location', 'date_posted', 'indeed_job_url', 'company_job_url_link', 'salary', 'fully_remote'])

page_suffix = "&start="
for i in range(num_res_pages):
    cur_pg_suffix = (i - 1) * 10
    cur_pg_url = indeed_rem_py_44d + page_suffix + str(cur_pg_suffix)
    response = requests.get(cur_pg_url, headers=headers) 
    soup = BeautifulSoup(response.content, "html.parser")


    print(f"on pg {i+1}/{num_res_pages}")
    jobs = soup.find_all("div", class_="job_seen_beacon")
    for cur_job in jobs:
        curJobDict = {}
        # top half of info box
        job = cur_job.find("td", class_="resultContent")

        # Check if job is fully remote

        # Extract job title, company, and location
        base_job_elem = job.find("a", class_="jcs-JobTitle")
        title                  = base_job_elem.text.strip()
        curJobDict['title']    = title
        indeed_jnum            = base_job_elem.get("data-jk")
        indeed_html_job_prefix = "https://www.indeed.com/viewjob?&jk=" #"&vjk="
        indeed_job_url         = indeed_html_job_prefix + indeed_jnum
        curJobDict['indeed_job_url'] = indeed_job_url
        company_name = ""
        try:
            company_name           = job.find("span", class_="companyName").text.strip()
        except Exception as err:
            print(err)
            continue

        curJobDict['company_name'] = company_name

        location               = job.find("div", class_="companyLocation").text.strip()
        curJobDict['location'] = location

        gutter_elem            = cur_job.find("div", class_="result-footer")
        date_posted            = gutter_elem.find("span", class_="date").text.strip()
        curJobDict['date_posted'] = date_posted

        company_job_url_postfix = base_job_elem.get("href")  # links to company posting
        company_job_url_link = "indeed.com" + company_job_url_postfix
        curJobDict['company_job_url_link'] = company_job_url_link

        ## notes for future development to pull out
        # after going to the specific webpg with job posting showing details // more than likely this would be second pass
        # where first pass would jsut be to gather all the top level info
        # then could split the task for each individual job to go to do
        # multi proc or distributed kubernetes exp
        
        fully_remote         = False # til proven otherwise / potentially via remote being in location?

        salary = ""
        try:
            # for when the salary is provided by the employer
            ##  <div class="metadata salary-snippet-container">/div/div
            salary = job.find("div", class_="salaryOnly").find("div").find("div").text.strip()
        except AttributeError as wrongTypeErr:
            try:
                # else when the salary is estimated by indeed
                ## <div class="metadata estimated-salary-container"><span class="estimated-salary">
                salary = job.find("span", class_="estimated-salary").find("span").text.strip()
            except AttributeError as info_not_found_err:
                print(info_not_found_err)

        curJobDict['salary'] = salary if "$" in salary else ""

        base_misc_elem = job.find("div", class_="metadataContainer")
        misc_inf = []
        if base_misc_elem:
            misc_elems = base_misc_elem.find_all("div", class_="metadata")
            for cur_misc_elem in misc_elems:
                cur_misc_elem_text = cur_misc_elem.text.strip()
                misc_inf.append(cur_misc_elem_text)


        company_rating = ""
        try:
            company_rating = job.find("a", class_="ratingLink").text.strip()
        except Exception as generalErr:
            print(generalErr)


        # update dataframe with new jobinfo dictionary
        if company_name: # to prevent from pullin in garbage
            df_jobs.loc[len(df_jobs)] = curJobDict


        sleep(0.01)

df_jobs.to_excel("indeedsoup.xlsx", sheet_name='Indeed_2023')

end_time = time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.2f} seconds")
