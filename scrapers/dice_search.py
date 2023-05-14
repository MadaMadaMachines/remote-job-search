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
    chromeOptions.add_argument("--window-size=1920,1080");
    chromeOptions.add_argument("--disable-gpu");
    chromeOptions.add_argument("--disable-extensions");
    chromeOptions.add_argument("--proxy-server='direct://'");
    chromeOptions.add_argument("--proxy-bypass-list=*");
    chromeOptions.add_argument("--start-maximized");
    chromeOptions.add_argument("--headless");

    job_details_list = []

    RESPG_ITER_STUB = "!~!PG_ITER!~!"
    dice_base_url = "https://www.dice.com/jobs?q=python&radius=30&radiusUnit=mi&pageSize=20&filters.isRemote=true&language=en&page=!~!PG_ITER!~!"
    
    with webdriver.Chrome(chrome_options=chromeOptions) as driver:
   
        actChain   = ActionChains(driver)
        wait_time  = 5
        webwait    = WebDriverWait(driver, wait_time)
        MAX_RESULTS = 333  # to test out and get a feel of time to scan a page or avg time per result
        res_ctr     = 0
        is_first_page = True

        MAX_PGS = 111
        for pg_iter in range(1,MAX_PGS):
            url = dice_base_url.replace(RESPG_ITER_STUB, str(pg_iter) )
            #//*[@id="totalJobCount"]

            driver.get(url)
            sleep(1)
            if is_first_page:
                total_res = driver.find_element_by_xpath('//*[@id="totalJobCount"]').text.strip()
                print(f"Total # jobs found to scrap: {total_res}")
                is_first_page = False


            JOB_ITER_STUB = "!~!JOB_ITER!~!"

            job_listings = driver.find_elements(By.XPATH, '//div[contains(@class, "search-card")]')
            MAX_RES_PER_PG = 20
            result_iter = 0
            for job in job_listings:
                if result_iter >= MAX_RES_PER_PG:
                    print("\n\n\tPAGE BREAK \n\n")
                    break
                elif res_ctr >= MAX_RESULTS:
                    print(f"\n\n\tObtained {res_ctr} # of results!")
                    break
                    # likely a better way to handle this than double nested loop breaking after 9th result on pg to continue to next pg
                #cur_job_xpath = job_res_iter_xpath.replace(JOB_ITER_STUB, str(x+1) )
                #print(cur_job_xpath)
                sleep(1)


                company          = job.find_element(By.XPATH, './/a[contains(@data-cy, "search-result-company-name")]').text
                location         = job.find_element(By.XPATH, './/span[contains(@data-cy, "search-result-location")]').text   #"jobCard-location")]').text #job.find_element_by_css_selector('.location span').text

                posted_date      = job.find_element(By.XPATH, './/span[contains(@class, "posted-date")]').text  #job.find_element_by_css_selector('.posted-date').get_attribute('title')
                salary = None
                # dice doesn't include salary in top lvl info
                base_title_elem  = job.find_element(By.XPATH, './/a[contains(@class, "card-title-link")]')
                title            = base_title_elem.text #job.find_element_by_xpath().text # base_title_elem.text  #job.find_element_by_css_selector('.card-header a').text
                url_job_detailed = base_title_elem.get_attribute("href")
                #posted_date = datetime.datetime.strptime(posted_date, '%Y-%m-%dT%H:%M:%S')
                today = datetime.datetime.now()


                # Print job information
                print(f"Title: {title}\n\tCompany: {company}\n\tLocation: {location}" +
                  f"\n\tSalary: {salary}" +
                  f"\n\tDate Posted:  {posted_date}" +
                  f"\n\tDetailed Link:  {url_job_detailed}")

                result_iter += 1
                res_ctr+=1


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
       
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    end_time = time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.2f} seconds")

