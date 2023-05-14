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



def scrape_job_listings():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.headless = False #if debugWebDriver else True
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
    job_details_list = []
    RESPG_ITER_STUB = "!~!PG_ITER!~!"
    monster_url_base = 'https://www.monster.com/jobs/search?q=software-developer&where=remote&et=REMOTE&recency=last+month&page=!~!PG_ITER!~!'
    with webdriver.Chrome(chrome_options=chromeOptions) as driver:
        actChain   = ActionChains(driver)
        wait_time  = 15
        webwait    = WebDriverWait(driver, wait_time)
        MAX_RESULTS = 100 # to test out and get a feel of time to scan a page or avg time per result
        res_ctr     = 0
        for pg_iter in range(1,22):
            url = monster_url_base.replace(RESPG_ITER_STUB, str(pg_iter) )

            driver.get(url)
            sleep(1)
            #work for first but not siblings # job_listings = driver.find_elements(By.XPATH, '//article[contains(@class, "job-cardstyle_")]')
            ##
            ##num_jobs_on_pg = len(job_listings)
            #init_listing = job_listings[0]
            # INDEED_JOB_RES_XPATH = '//h2[contains(@class, "jobTitle")]/a'
            #self.webHandle.find_elements(By.XPATH, NEXT_RES_PG_XPATH)
            # GOOD til HERE


            #init_listing_elem = job_res_box_elem.find_element(By.XPATH, '//article[contains(@class, "job-cardstyle_")]')

            #job_res_iter_xpath ='/article[!~!JOB_ITER!~!]'
            JOB_ITER_STUB = "!~!JOB_ITER!~!"
            ## children elements willbe the various article boxes beneath
            ## the next trouble is how to iterate thru pages with infintie scroll
            ##  given that monster supports pg num in url- need to keep this mind as will be helpful
            on_first_elem = True
            # so firefox displays using article html tag vs chrome using a
            # could generalize to * though that just feels... wrong
            article_iter = '/html/body/div/div[2]/main/div[3]/nav/section[1]/div[2]/div/div/div/div[!~!JOB_ITER!~!]'
            #"a[!~!JOB_ITER!~!]" #"article[!~!JOB_ITER!~!]"

            job_listings = driver.find_elements(By.XPATH, '//div[contains(@class, "job-search-results")]')
            MAX_RES_PER_PG = 9
            result_iter = 0
            for job in job_listings:
                if result_iter >= MAX_RES_PER_PG:
                    print("\n\n\tPAGE BREAK \n\n")
                    break
                elif res_ctr >= MAX_RESULTS:
                    print(f"\n\n\tObtained {res_ctr} # of results!")
                    break
                    # likely a better way to handle this than double nested loop breaking after 9th result on pg to continue to next pg

                sleep(1)
                #webwait.until( ExpCond.presence_of_element_located((By.XPATH, cur_jobbox_xpath)), wait_time)


                company          = job.find_element(By.XPATH, './/h3[contains(@data-test-id, "svx-job-company")]').text #@class, "JobCardCompany")]').text  
                location         = job.find_element(By.XPATH, './/p[contains(@data-test-id, "svx-job-location")]').text   #"jobCard-location")]').text #job.find_element_by_css_selector('.location span').text

                posted_date      = job.find_element(By.XPATH, './/span[contains(@data-test-id, "svx-job-date")]').text  #job.find_element_by_css_selector('.posted-date').get_attribute('title')
                salary = None
                try:
                    salary           = job.find_element(By.XPATH, './/p[contains(@data-test-id, "svx-job-salary")]').text
                except Exception as e:
                    print(e)

                base_title_elem  = job.find_element(By.XPATH, './/a[contains(@class, "JobCardTitle")]')
                title            = base_title_elem.text  #job.find_element_by_css_selector('.card-header a').text
                url_job_detailed = base_title_elem.get_attribute("href")
                today = datetime.datetime.now()

                # Print job information
                print(f"Title: {title}\n\tCompany: {company}\n\tLocation: {location}" +
                  f"\n\tSalary: {salary}" +
                  f"\n\tDate Posted:  {posted_date}" +
                  f"\n\tDetailed Link:  {url_job_detailed}")

                result_iter += 1

            if res_ctr >= MAX_RESULTS:
                print(f"\n\n\tObtained {res_ctr} # of results!")
                break
        driver.close()
        driver.quit()
        print(f"# results: {num_res}")
    return job_details_list


if __name__ == '__main__':
    start_time = time()
    try:
        base_url = 'https://www.monster.com'

        job_listings = scrape_job_listings()

    except Exception as e:
        print(e)
        print(traceback.format_exc())

    end_time = time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    # 15pg , 9res/pg, 410.28s
    # 135 res in 410.28s = 3.03911111sec per high lvl res scrape

