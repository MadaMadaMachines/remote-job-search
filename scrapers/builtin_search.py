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
from selenium.webdriver.firefox.options import Options


def scrape_job_listings():
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    driver = webdriver.Firefox(options=options)

    chromeOptions = webdriver.ChromeOptions()
    ffOptions = webdriver.FirefoxOptions()
    ffOptions.add_argument("--binary 'C:/Program Files/Mozilla Firefox/firefox.exe'");
    headless= False
    if headless:
        ffOptions.add_argument("--window-size=1920,1080");
        ffOptions.add_argument("--disable-gpu");
        ffOptions.add_argument("--disable-extensions");
        ffOptions.add_argument("--proxy-server='direct://'");
        ffOptions.add_argument("--proxy-bypass-list=*");
        ffOptions.add_argument("--start-maximized");
        ffOptions.add_argument("--headless");

    else: # see what is happening
        ffOptions.headless = False 
        ffOptions.add_argument('--window-size=1920,1080')
        ffOptions.add_argument("--start-maximized")
        ffPrefs = {   "download.default_directory" : DL_DIR,
                          "download.download_directory" : DL_DIR,
                          "download.download_dir" : DL_DIR,
                          "download.prompt_for_download" : True,
                          "download.directory_upgrade" : True,
                          "download_restrictions" : 0,
                          "safebrowsing_for_trusted_sources_enabled" : False,
                          }
       

    job_details_list = []
    RESPG_ITER_STUB = "!~!PG_ITER!~!"
    builin_base_url = "https://builtin.com/jobs/remote?search=python&page=!~!PG_ITER!~!"
    
    with webdriver.Firefox(firefox_options=options) as driver:
    
        actChain   = ActionChains(driver)
        wait_time  = 22
        webwait    = WebDriverWait(driver, wait_time)
        driver.implicitly_wait(wait_time)
        MAX_RESULTS = 333  # to test out and get a feel of time to scan a page or avg time per result
        res_ctr     = 0
        
        is_first_page = True

        MAX_PGS = 11  # make this dynamic based on results for init run
        ## then make it based on limit til hit repeats in db
        for pg_iter in range(1,MAX_PGS):
            url = builin_base_url.replace(RESPG_ITER_STUB, str(pg_iter) )

            print(url)
            print("\n\n")
            driver.get(url)
            sleep(5) ## even with the wait until, hard wait seemingly solves issues- maybe waiting on wrong elem
            webwait.until( ExpCond.presence_of_element_located((By.XPATH, './/div[contains(@class,"count")]/b')), wait_time)

            if is_first_page:
                title_something_elem = driver.find_element_by_xpath('.//div[contains(@class,"count")]')
                total_res = title_something_elem.find_element_by_xpath(".//b[1]").text.strip()


                print(f"Total # jobs found to scrap: {total_res}")
                is_first_page = False

            JOB_ITER_STUB = "!~!JOB_ITER!~!"
            job_listings = driver.find_elements(By.XPATH, '//div[contains(@class,"job-item")]')
            num_listing = len(job_listings)
            print(f"# listing found on page: {num_listing} \n\n")
            MAX_RES_PER_PG = 13
            result_iter = 0
            for job in job_listings:
                if result_iter >= MAX_RES_PER_PG:
                    print("\n\n\tPAGE BREAK \n\n")
                    break
                elif res_ctr >= MAX_RESULTS:
                    print(f"\n\n\tObtained {res_ctr} # of results!")
                    break
                    # likely a better way to handle this than double nested loop breaking after 9th result on pg to continue to next pg
                
                sleep(.333)
                company = None

                try:
                    company          = job.find_element(By.XPATH, './/div[contains(@class, "company-title")]').text
                except StaleElementReferenceException as stale_err:
                    temp_job_elems = driver.find_elements(By.XPATH, '//div[contains(@class,"job-item")]')
                    job = temp_job_elems[result_iter + 1]
                    company          = job.find_element(By.XPATH, './/div[contains(@class, "company-title")]').text


                location = None
                try:
                    location         = job.find_element(By.XPATH, './/div[contains(@class, "info-label location")]').text   #"jobCard-location")]').text #job.find_element_by_css_selector('.location span').text
                except Exception as e:
                    pass

                remote_loc = None
                try:
                    remote_loc         = job.find_element(By.XPATH, './/div[contains(@class, "info-label remote")]').text   #"jobCard-location")]').text #job.find_element_by_css_selector('.location span').text
                except Exception as e:
                    pass

                posted_date = None
                try:
                    posted_date      = job.find_element(By.XPATH, './/div[contains(@class, "info-label age")]').text  #job.find_element_by_css_selector('.posted-date').get_attribute('title')
                except Exception as e:
                    pass

                salary = None
                title            = job.find_element(By.XPATH, './/h2[@class="job-title"]').text.strip()  ##base_title_elem.text #job.find_element_by_xpath().text # base_title_elem.text  
                url_job_detailed = job.find_element(By.XPATH, './/a[contains(@class, "job-details-link")]').get_attribute("href")
                today = datetime.datetime.now()


                # Print job information
                print(f"Title: {title}\n\tCompany: {company}\n\tLocation: {location}" +
                  f"\n\tRemote: {remote_loc}\n\tSalary: {salary}" +
                  f"\n\tDate Posted:  {posted_date}" +
                  f"\n\tDetailed Link:  {url_job_detailed}")

                result_iter += 1
                res_ctr+=1
                driver.execute_script("window.scrollBy(0,200)","")


            if res_ctr >= MAX_RESULTS:
                print(f"\n\n\tObtained {res_ctr} # of results!")
                break
        driver.close()
        driver.quit()
        print(f"# results: {res_ctr}")
    return job_details_list



if __name__ == '__main__':
    start_time = time()
    try:
        job_listings = scrape_job_listings()
        # doesn't return anything atm just prints

    except Exception as e:
        print(e)
        print(traceback.format_exc())

    end_time = time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.2f} seconds")

