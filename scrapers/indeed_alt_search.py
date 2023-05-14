from math import ceil
from os import walk, listdir
import os
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import \
    TimeoutException, NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpCond
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options

from pynput.keyboard import Key, Controller

from job_details import job_details

# selenium version of indeed search


INDEED_CO_LOOKUP_PG  = "https://www.indeed.com/companies"
INDEED_LOGIN_PG = "https://secure.indeed.com/auth?hl=en_US&co=US"
#INDEED_REM_PY_SE = "https://www.indeed.com/jobs?q=software+engineer&l=Remote&rbl=Remote&fromage=44&jlid=aaa2b906602aa8f5"
#within last 44 days / fromage param
INDEED_AGE_LIMIT = "&fromage=44"
INDEED_REMOTE_LOC_SEARCH = "&l=Remote&rbl=Remote"
INDEED_REMOTE_LOC_FILTER = "&jlid=aaa2b906602aa8f5"
INDEED_BASE_JOB_QUERY = "https://www.indeed.com/jobs?q=software+engineer"
INDEED_SORT_BY_DATE = "&sort=date"
INDEED_REM_PY_SE = INDEED_BASE_JOB_QUERY + INDEED_REMOTE_LOC_SEARCH + INDEED_REMOTE_LOC_FILTER + INDEED_AGE_LIMIT + INDEED_SORT_BY_DATE
# https://www.indeed.com/jobs?q=software+engineer&l=Remote&rbl=Remote&jlid=aaa2b906602aa8f5&fromage=44&sort=date
ANGEL_CANDIDATE_LOGIN = "https://angel.co/login"
ANGEL_COMPANY_LOGIN = "https://angel.co/v/login"
DEFAULT_WAIT  = 0.5  # ~500 milliseconds // 50 milliseconds runs into troubles of page not loaded before trying to move on
DL_DIR = "C:\\Users\\Human_001B\\Documents\\__code__\\useful_job_search"

XL_WAIT = 22
LONG_WAIT = 11
MED_WAIT = 7
SMED_WAIT = 5
SM_WAIT = 3
SEC_WAIT = 1
DEMIMIN_WAIT = 30
MIN_WAIT = 60


INDEED_CO_NAME_XPATH = '//div[@class="jobsearch-InlineCompanyRating-companyHeader"]/a' # not working suddenly 27-11-2022
INDEED_CO_NAME_XPATH = './/*[contains(@class,"jobsearch-InlineCompanyRating-companyHeader")]'
INDEED_CO_NAME_CSS_SEL = 'div.jobsearch-InlineCompanyRating'
INDEED_CO_RATING_XPATH = './/*[contains(@class,"icl-Ratings-starsCountWrapper")]'
#'//a[@class="icl-Ratings-starsCountWrapper icl-Ratings-link"]'
INDEED_JOB_NAME_CSSPATH = 'div#jobsearch-Main > div > div > div:nth-of-type(5) > div:nth-of-type(2) > div > div > div > div > div > div > div > div:nth-of-type(1) > div > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > h1'
INDEED_JOB_NAME_XPATH = '//*[contains(@class, "jobsearch-JobInfoHeader-title-container")]/h2'  #previously was h1, seemingly changed to h2 in feb2023
CO_RATING_VAL_XPATH = '//meta[@itemprop="ratingValue")]'
CO_RATING_VOTES_XPATH = '//meta[@itemprop="ratingCount")]'
INDEED_JOB_SALARY_XPATH = '//div[@id="salaryInfoAndJobType"]'
INDEED_JOB_SALEST_XPATH = '// li[contains(text(), "Indeed\'s estimated salary")]'

NUM_SEARCH_RES_XPATH = '//div[@class="jobsearch-JobCountAndSortPane-jobCount"]/span[1]'
NEXT_RES_PG_XPATH = '//a[@aria-label="Next Page"]'

INDEED_JOB_DEET_XPATH_ORIGINAL = '//div[@id="mosaic-provider-jobcards"]/ul[1]/li[!~!JOB_ITER!~!]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/h2[1]/a[1]'
INDEED_JOB_DEET_XPATH = '//div[@class="mosaic-zone"]/div/ul[1]/li[!~!JOB_ITER!~!]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/h2[1]/a[1]'
INDEED_JOB_DEET_ROOT_XPATH ='//div[@class="mosaic-zone"]/div/ul[1]/li'

INDEED_JOB_RES_XPATH = '//h2[contains(@class, "jobTitle")]/a'
#'//div[@id="mosaic-provider-jobcards"]/ul[1]/li[1]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/h2[1]/a[1]'
# default 15jobs per page
JOB_ITER_PLACEHOLDER = "!~!JOB_ITER!~!"
 # since indeed starts at one

class ghost_driver():
    def __init__(self, browser_handle=None, dataSite=INDEED_REM_PY_SE, debugWebDriver = True):


        # setup webhandle
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.headless = False if debugWebDriver else True
        chromeOptions.add_argument("--start-maximized")
        if chromeOptions.headless:
            chromeOptions.add_argument('--window-size=1920,1080')

        chromePrefs = {   "download.default_directory" : DL_DIR,
                          "download.download_directory" : DL_DIR,
                          "download.download_dir" : DL_DIR,
                          "download.prompt_for_download" : True,
                          "download.directory_upgrade" : True,
                          "download_restrictions" : 0,
                          "safebrowsing_for_trusted_sources_enabled" : False,
                          #"detach": True,
                          }
        chromeOptions.add_experimental_option("prefs", chromePrefs)
        self.webHandle  = webdriver.Chrome(chrome_options=chromeOptions) 

        self.targetSite = dataSite
        self.wait       = WebDriverWait(self.webHandle, XL_WAIT)
        self.actChain   = ActionChains(self.webHandle)

        self.keyboard   = Controller()
        self.job_iter   = 0 # indeed starts at 1 and defualts to max 15 per page
        self.res_count = 0


    def process_results(self):
        self.go_to_job_query_res()
        while self.job_iter < self.res_count:
            self.comb_cur_pg()
            self.go_to_next_results_pg()
            self.job_iter += 15


    def go_to_next_results_pg(self):
        NEXT_RES_PG_XPATH = '//a[@aria-label="Next Page"]'
        next_res_pg_elem = self.webHandle.find_elements(By.XPATH, NEXT_RES_PG_XPATH)[0]
        next_res_pg_elem.click()
        #sleep(SMED_WAIT)

    def go_to_job_query_res(self):
        print("loading website")
        self.webHandle.get(self.targetSite)
        #sleep(DEFAULT_WAIT)
        print("got to website")
        num_res_elem = self.webHandle.find_elements(By.XPATH, NUM_SEARCH_RES_XPATH)[0]
        print(num_res_elem.text)
        self.res_count = int( num_res_elem.text.replace(",", "").replace(" jobs", "").strip() )
        print(self.res_count)


    def comb_cur_pg(self):
        max_jobs_per_pg = 15
        max_links_per_pg = 18 # given link for every 5, 15+(15/5)=18 with every 6 being skipworthy ad

        job_list_box_height = 311 # in pixels
        buffer_pixels = job_list_box_height * (1/ 3)
        center_px = 0

        for job_iter in range(max_links_per_pg):
            cur_xpath = INDEED_JOB_DEET_XPATH_ORIGINAL.replace(JOB_ITER_PLACEHOLDER, str(job_iter+1))
            print(cur_xpath)
            try:
                cur_job_link_elem = self.webHandle.find_element_by_xpath(cur_xpath)
                print(cur_job_link_elem.text)
                rand_pxl_offset = 0

                scroll_multiplier = 1.2 if (job_iter > 0) else 0
                self.webHandle.execute_script("window.scrollBy(0,"+str(job_list_box_height * scroll_multiplier)+")","")
                cur_job_link_elem.click()

                sleep(SEC_WAIT*3)

                self.wait.until( ExpCond.presence_of_element_located((By.XPATH, INDEED_JOB_NAME_XPATH)), LONG_WAIT )

                job_deet_suffix_to_rem = "- job post" # since removing new lines removes prefix single space before hyphen #" - job post"
                job_title_ele = self.webHandle.find_element_by_xpath(INDEED_JOB_NAME_XPATH)
                exp_cur_job_link_title_base = cur_job_link_elem.text
                act_job_deet_title_base = job_title_ele.text
                act_job_deet_title_formatted = act_job_deet_title_base.replace("\n","").replace("\r","").replace(job_deet_suffix_to_rem, "")
                job_title = act_job_deet_title_base.split(" - ")[0].strip()
                cur_job_link_title = exp_cur_job_link_title_base.split(" - ")[0].strip()
                print("\tcur link: {0}\n\tact link: {1}".format(exp_cur_job_link_title_base, act_job_deet_title_base))


                while act_job_deet_title_formatted != exp_cur_job_link_title_base:
                    ## this implementation seemingly consistently works
                    ##  ToDo figure out if it is b/c of the scrollBy or elem.click() or combo
                    # !!! --> potential infinite loop if it never gets coorect match <--- !!!
                    sleep(SEC_WAIT) # was SM_WAIT
                    self.actChain.move_to_element_with_offset(cur_job_link_elem, center_px, center_px )
                    self.actChain.perform()
                    self.actChain.reset_actions()
                    self.webHandle.execute_script("window.scrollBy(0,500)","")
                    sleep(SEC_WAIT)
                    cur_job_link_elem.click() # ?excess


                    self.wait.until( ExpCond.presence_of_element_located((By.XPATH, INDEED_JOB_NAME_XPATH)) )
                    #self.wait.until( ExpCond.presence_of_element_located((By.CSS_SELECTOR, INDEED_JOB_NAME_CSSPATH)) )
                    job_title_ele = self.webHandle.find_element_by_xpath(INDEED_JOB_NAME_XPATH)
                    act_job_deet_title_base = job_title_ele.text.replace(job_deet_suffix_to_rem, "")
                    act_job_deet_title_formatted = act_job_deet_title_base.replace("\n","").replace("\r","").replace(job_deet_suffix_to_rem, "")
                    job_title = act_job_deet_title_base.split(" - ")[0].strip()
                    print("-+-+"*11)
                    print("\tcur link: {0}\n\tact link: {1}".format(exp_cur_job_link_title_base, act_job_deet_title_formatted))
                sleep(SEC_WAIT)
                self.pull_job_info()

            # every sixth is ad, but incase this changes
            # safer to do this as try/except
            except NoSuchElementException as ghostErr:
                print(ghostErr)
                self.actChain.reset_actions()



    def pull_job_info(self):
        job_title_ele = self.webHandle.find_element_by_xpath(INDEED_JOB_NAME_XPATH)
        job_title = job_title_ele.text.split("-")[0].strip()
        print(job_title)

        
        sleep(SEC_WAIT)
        company_name_ele = self.webHandle.find_element_by_css_selector(INDEED_CO_NAME_CSS_SEL)
        # handle case in which reached race condition or other error
        TIMEOUT_LIMIT = 10
        timeout_ctr = 0
        while not company_name_ele:
            sleep(SEC_WAIT)
            timeout_ctr += 1
            company_name_ele = self.webHandle.find_element_by_css_selector(INDEED_CO_NAME_CSS_SEL)
            if timeout_ctr > TIMEOUT_LIMIT:
                raise Exception("failed to find company name and glean info")
        company_name = company_name_ele.text
        print(company_name)

        ## pull company rating details / if available
        try:

            self.wait.until( ExpCond.presence_of_element_located((By.XPATH, INDEED_CO_RATING_XPATH)) , MED_WAIT) # was MIN_WAIT
            company_rating_ele = self.webHandle.find_element_by_xpath(INDEED_CO_RATING_XPATH)
            print(company_rating_ele.get_attribute("aria-label")) # rating value & number votes

        except (NoSuchElementException, TimeoutException) as not_ere_err:
            print("{0} does not have a rating that could be found".format(company_name) )
        job_salary_elem = ""

        ## grab given salary info or indeed's estimate
        try:

            self.wait.until( ExpCond.presence_of_element_located((By.XPATH, INDEED_JOB_SALARY_XPATH)), SM_WAIT)
            job_salary_elem = self.webHandle.find_element_by_xpath(INDEED_JOB_SALARY_XPATH)
            print(job_salary_elem.text)

        except (NoSuchElementException, TimeoutException) as not_ere_err:
            print("{0} {1} does not have a salary that could be found".format(company_name, job_title) )

        if (isinstance(job_salary_elem, str) and '$' not in job_salary_elem) \
        or (isinstance(job_salary_elem, WebElement) and '$' not in job_salary_elem.text):
            print("attempting to find indeed estimate for {0} {1} ".format(company_name, job_title) )
            try:
                self.wait.until( ExpCond.presence_of_element_located((By.XPATH, INDEED_JOB_SALEST_XPATH)), SM_WAIT)
                job_salest_elem = self.webHandle.find_element_by_xpath(INDEED_JOB_SALEST_XPATH)
                print(job_salest_elem.text)
            except (NoSuchElementException, TimeoutException) as not_ere_err:
                print("{0}  {1} does not have a salary estimate that could be found, delaying salary info ...for now".format(company_name,job_title) )


        print("  -  "*22)



def main():
    test = ghost_driver(debugWebDriver=True)
    test.process_results()

if __name__ == '__main__':
    main()