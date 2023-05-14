import datetime
import traceback
from time import sleep, time

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

DRIVER_PATH = 'path/to/chromedriver.exe'
DL_DIR = "C:\\Users\\Human_001B\\Documents\\__code__\\useful_job_search"


def scrape_job_listings():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions = webdriver.ChromeOptions()
    headless= False
    if headless:
        chromeOptions.add_argument("--window-size=1920,1080");
        chromeOptions.add_argument("--disable-gpu");
        chromeOptions.add_argument("--disable-extensions");
        chromeOptions.add_argument("--proxy-server='direct://'");
        chromeOptions.add_argument("--proxy-bypass-list=*");
        chromeOptions.add_argument("--start-maximized");
        chromeOptions.add_argument("--headless");

    else: # see what is happening
        chromeOptions.headless = False 
        chromeOptions.add_argument('--window-size=1920,1080')
        chromeOptions.add_argument("--start-maximized")
        chromePrefs = {   "download.default_directory" : DL_DIR,
                          "download.download_directory" : DL_DIR,
                          "download.download_dir" : DL_DIR,
                          "download.prompt_for_download" : True,
                          "download.directory_upgrade" : True,
                          "download_restrictions" : 0,
                          "safebrowsing_for_trusted_sources_enabled" : False,

                          }
        chromeOptions.add_experimental_option("prefs", chromePrefs)



    job_details_list = []
    RESPG_ITER_STUB = "!~!PG_ITER!~!"
    ventureloop_url = "https://www.ventureloop.com/ventureloop/job_search.php?g=0&kword=python&jcat=%&dc=all&ldata=%&jt=1&jd=1&remote=work_remotely&d=5&btn=1"

    with webdriver.Chrome(chrome_options=chromeOptions) as driver:
        actChain   = ActionChains(driver)
        wait_time  = 5
        webwait    = WebDriverWait(driver, wait_time)
        driver.implicitly_wait(wait_time*3)
        MAX_RESULTS = 333  # to test out and get a feel of time to scan a page or avg time per result
        res_ctr     = 0
        is_first_page = True

        MAX_PGS = 111
        for pg_iter in range(1,MAX_PGS):
            url = ventureloop_url 

            if is_first_page:
                driver.get(url)  
                sleep(7)  ## ToDo see if can swap hard time wait for implicit wait
                job_res_elem = driver.find_element_by_xpath('//div[@id="job_search_results"]/div/form')

                total_res = job_res_elem.find_element_by_xpath('.//div[@class="labelText"]').text.strip()
                print(f"Total # jobs found to scrap: {total_res}")
                is_first_page = False
            else:
                sleep(7)


            JOB_ITER_STUB = "!~!JOB_ITER!~!"
            job_res_tbl_elem = driver.find_element_by_xpath('.//table')
            job_listings = job_res_tbl_elem.find_elements(By.XPATH, './/tr')

            MAX_RES_PER_PG = 25
            result_iter = 0

            date_index    = 0
            title_index   = 1
            company_index = 2
            vc_index      = 3
            loc_index     = 4
            for job in job_listings:
                if result_iter >= MAX_RES_PER_PG:
                    print("\n\n\tPAGE BREAK \n\n")
                    break
                elif res_ctr >= MAX_RESULTS:
                    print(f"\n\n\tObtained {res_ctr} # of results!")
                    break
                elif job.get_attribute('class') == "head":
                    pass
                else:
                    # likely a better way to handle this than double nested loop breaking after 9th result on pg to continue to next pg

                    sleep(1)
                    job_details_elem = job.find_elements(By.XPATH, './/td')


                    location         = job_details_elem[loc_index].text
                    posted_date      = job_details_elem[date_index].text
                    salary = None

                    company_base_elem  = job_details_elem[company_index]
                    company            = company_base_elem.text
                    company_link       = company_base_elem.find_element_by_xpath('.//a').get_attribute("href")

                    base_title_elem  = job_details_elem[title_index]
                    title            = base_title_elem.text 
                    url_job_detailed = base_title_elem.find_element_by_xpath('.//a').get_attribute("href")

                    base_vc_elem          = job_details_elem[vc_index]
                    vc_name = base_vc_elem.text
                    vc_link = base_vc_elem.find_element_by_xpath('.//a').get_attribute("href")
                    today = datetime.datetime.now()


                    # ToDo - update this to pandas df for csv/excel output directly
                    print(f"Title: {title}\n\tCompany: {company} - {company_link}\n\tLocation: {location}" +
                      f"\n\tSalary: {salary}" +
                      f"\n\tDate Posted:  {posted_date}" +
                      f"\n\tDetailed Link:  {url_job_detailed}"+
                      f"\n\tVC Name + Link: {vc_name} - {vc_link}" +
                      "\n\n\n")


                    result_iter += 1
                    res_ctr+=1



            if res_ctr >= MAX_RESULTS:
                print(f"\n\n\tObtained {res_ctr} # of results!")
                break
            print("\n\attempting to go to pg "+str(pg_iter+1)+"\n")
            pg_nav_elems = driver.find_element_by_xpath('//div[contains(@class,"dataTables_paginate")]')
            next_btn_elem  = pg_nav_elems.find_element_by_xpath(".//a[contains(@id, "+str(pg_iter+1)+")]") ##'>')]")  #>›<
            
            next_btn_elem.click()


        driver.close()
        driver.quit()
        print(f"# results: {res_ctr}")
    return job_details_list



if __name__ == '__main__':
    start_time = time()
    try:
        # doesn't return anything atm just prints
        job_listings = scrape_job_listings()
       
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    end_time = time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.2f} seconds")

