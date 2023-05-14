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
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options



def scrape_job_listings():
    ffOptions = webdriver.FirefoxOptions()
    ffOptions.add_argument("--binary 'C:/Program Files/Mozilla Firefox/firefox.exe'");
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'


    job_details_list = []
    RESPG_ITER_STUB = "!~!PG_ITER!~!"
    startupjobs_base_url = "https://startup.jobs/?q=python&remote=true&page=!~!PG_ITER!~!"

    with webdriver.Firefox(firefox_options=options) as driver:

        actChain   = ActionChains(driver)
        wait_time  = 15
        webwait    = WebDriverWait(driver, wait_time)
        driver.implicitly_wait(wait_time)

        MAX_RESULTS = 333  # to be updated by date posted limit- ie not to scan past jobs more than 1 month old in posting age
        res_ctr     = 0
        is_first_page = True

        MAX_PGS = 11
        for pg_iter in range(1,MAX_PGS):
            url = startupjobs_base_url.replace(RESPG_ITER_STUB, str(pg_iter) )

            driver.get(url)
            sleep(wait_time)
            if is_first_page:
                res_box = driver.find_element_by_xpath('//div[contains(@class,"grid-cols-2 gap-2 p-2")]')
                res_types_elems = res_box.find_elements_by_xpath('.//label[@class="block"]')
                ft_index = 0
                pt_index = 1
                intern_index = 2
                contractor_index = 3

                total_res = res_types_elems[ft_index].text.strip()
                print(f"Total # FT jobs found to scrap: {total_res}")

                total_pt_res = res_types_elems[pt_index].text.strip()
                print(f"Total # PT jobs found to scrap: {total_pt_res}")

                total_ires = res_types_elems[intern_index].text.strip()
                print(f"Total # intern jobs found to scrap: {total_ires}")

                total_cres = res_types_elems[contractor_index].text.strip()
                print(f"Total # contractor jobs found to scrap: {total_cres}")

                is_first_page = False


            JOB_ITER_STUB = "!~!JOB_ITER!~!"

            job_listings = driver.find_elements_by_xpath('//div[contains(@data-search-target, "results")]//div[contains(@data-mark-visited-links-target, "container")]')
            MAX_RES_PER_PG = 25
            result_iter = 0
            for job in job_listings:
                if result_iter >= MAX_RES_PER_PG:
                    print("\n\n\tPAGE BREAK \n\n")
                    break
                elif res_ctr >= MAX_RESULTS:
                    print(f"\n\n\tObtained {res_ctr} # of results!")
                    break
                    # likely a better way to handle this than double nested loop breaking after 9th result on pg to continue to next pg
                    # could remove outter loop and look for next pg element 

                sleep(1)

                company_base_elem  = job.find_element(By.XPATH,".//a[contains(@class, 'z-10 hover:underline py-1')][contains(@href, '/@')]")
                company            = company_base_elem.get_attribute('text').strip()
                company_link       = company_base_elem.get_attribute("href")


                location         = job.find_element(By.XPATH, './/div[contains(@data-post-template-target, "location")]/a').get_attribute('text')  

                posted_date      = None # not avilail high lvl on startup jobs
  
                salary = None
                tags_list = []
                tags_container = job.find_element(By.XPATH,'.//div[contains(@data-post-template-target, "tags")]')
                tags_elem_list = tags_container.find_elements_by_xpath('.//a')
                for cur_tag_elem in tags_elem_list:
                    cur_tag_text = cur_tag_elem.get_attribute('text').strip()
                    tags_list.append(cur_tag_text)

                base_title_elem  = job.find_element(By.XPATH, './/a[contains(@data-mark-visited-links-target, "anchor")]')
                title            = base_title_elem.get_attribute('text').replace("✓","").replace("\n", "").replace("\r", "").strip() #job.find_element_by_xpath().text # base_title_elem.text  #job.find_element_by_css_selector('.card-header a').text
                url_job_detailed = base_title_elem.get_attribute("href")
                #posted_date = datetime.datetime.strptime(posted_date, '%Y-%m-%dT%H:%M:%S')
                today = datetime.datetime.now()


                # ToDo - update this to pandas df for csv/excel output directly
                print(f"\tTitle: {title}\n\t  Company: {company}    -   {company_link} \n\t  Location: {location}" +
                  f"\n\t  Salary: {salary}" +
                  f"\n\t  Job Tags:  {tags_list}" +
                  f"\n\t  Detailed Link:  {url_job_detailed}" +
                  "\n\n")

                result_iter += 1
                res_ctr+=1

            if res_ctr >= MAX_RESULTS:
                print(f"\n\n\tObtained {res_ctr} # of results!")
                break

            print("\n\attempting to go to pg "+str(pg_iter+1)+"\n")
        driver.close()
        driver.quit()
        print(f"# results: {res_ctr}")
    return job_details_list


if __name__ == '__main__':
    start_time = time()
    try:


        job_listings = scrape_job_listings()
        # doesn't return anything atm just prints
        # need to update to use dataclass to store job details
        # then overwrite default to string and use that
        # potentially build in the job_details object to pandas df in job_catalog object where 1:N job_catalog to job_details
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    end_time = time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.2f} seconds")

