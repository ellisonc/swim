from selenium import webdriver
import re
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from bs4 import BeautifulSoup
import time



#**************************************************************************************************
# submitForm
#
# submit the initial form to usaswimming
#
#**************************************************************************************************
def submitForm(firstName, lastName, driver):
    try:
        fname_field = driver.find_element_by_name('FirstName')
        lname_field = driver.find_element_by_name('LastName')
        startDate = driver.find_element_by_name('UsasTimeSearchIndividual_Index_Div_1StartDate')
        endDate = driver.find_element_by_name('UsasTimeSearchIndividual_Index_Div_1EndDate')
        submit  = driver.find_element_by_id('UsasTimeSearchIndividual_Index_Div_1-saveButton')

        fname_field.send_keys(firstName)
        lname_field.send_keys(lastName)

        submit.click()
    except:
        print("There has been a problem submitting form to database. Try again")



#**************************************************************************************************
# scrapeAndSave
#
# Perform the actual time scraping and save to txt file... eventually a database
#
#**************************************************************************************************
def scrapeAndSave(driver):
    pageNum = 1
    numPages = int(driver.find_element_by_id("UsasTimeSearchIndividual_TimeResults_Grid-1-UsasGridPager-lblTotalPages").text)
    nxtPageBtn = driver.find_element_by_id("UsasTimeSearchIndividual_TimeResults_Grid-1-UsasGridPager-pgNext")
    browserPgNum = driver.find_element_by_id("UsasTimeSearchIndividual_TimeResults_Grid-1-UsasGridPager-txtCurrentPage")
    numPages = 1 #TODO temporary
    while(pageNum <= numPages):
        bsObj = BeautifulSoup(driver.page_source, "lxml")
        #parse table
        eventTable = bsObj.find("div", {"class":"k-grid-content-locked"}).table.tbody
        dataTable = bsObj.find("tbody", {'role':'rowgroup'})

        print(eventTable)
        print()
        print(dataTable)
        print()
        print()

        pageNum += 1
        if(pageNum <= numPages):
            nxtPageBtn.click()
            #wait for update
            for i in range(50):
                try:
                    current = int(browserPgNum.get_attribute('value'))
                except:
                    print("value was none")

                if(current == pageNum):
                    break

                if(i == 49):
                    print("Page load timed out")
                    return False
                else:
                    time.sleep(0.1)
    return True


#**************************************************************************************************
# getTimes
#
# Retrieve times from usaswimming database based on name only
#
#**************************************************************************************************
def getTimes(firstName, lastName):
    success = False
    #header = DesiredCapabilities.PHANTOMJS.copy()
    #header['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
    #                                                              'AppleWebKit/537.36 (KHTML, like Gecko) ' \
    #                                                              'Chrome/39.0.2171.95 Safari/537.36'
    #driver = webdriver.PhantomJS(executable_path='C:\Phantom\phantomjs.exe', desired_capabilities=header)
    driver = webdriver.Chrome(executable_path="C:\Chrome\chromedriver.exe")
    driver.get("https://www.usaswimming.org/Home/times/individual-times-search")

    #Submit the initial form
    submitForm(firstName, lastName, driver)

    time.sleep(1)   #wait for the response
    pageSource = driver.page_source
    bsObj = BeautifulSoup(pageSource, "lxml")

    clubTable = None
    try:
        clubTable = driver.find_element_by_id("UsasTimeSearchIndividual_PersonSearchResults_Grid-1")
    except:
        print("swimmer found?")


    table = bsObj.find("tbody", {"role":"rowgroup"})
    if(clubTable is not None):
        count = 0
        for row in table.children:
            print(str(count) + " " + row.td.next_sibling.text)
            count += 1
            print("")

        print(count)
        success = False
    else:
        print("User found")
        success = scrapeAndSave(driver)

    driver.close()
    return success
#End getTimes


#**************************************************************************************************
# getTimes_club
#
# Retrieve times from the usaswimming database based on name and team
#
#**************************************************************************************************
def getTimes_club(firstName, lastName, clubID):
    success = False
    #header = DesiredCapabilities.PHANTOMJS.copy()
    #header['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
    #                                                              'AppleWebKit/537.36 (KHTML, like Gecko) ' \
    #                                                              'Chrome/39.0.2171.95 Safari/537.36'
    #driver = webdriver.PhantomJS(executable_path='C:\Phantom\phantomjs.exe', desired_capabilities=header)
    driver = webdriver.Chrome(executable_path="C:\Chrome\chromedriver.exe")
    driver.get("https://www.usaswimming.org/Home/times/individual-times-search")

    #submit the initial form
    submitForm(firstName, lastName, driver)

    time.sleep(1)

    try:
        links = driver.find_elements_by_class_name('pointer')
    except:
        print("no pointers")
        return False

    if(len(links) <= clubID):
        print("Invalid Club ID")
        return False

    links[clubID].click()

    time.sleep(1)

    #get and store time information
    success = scrapeAndSave(driver)
    
    input("press key to continue")
    driver.close()
    return success
#End getTimes


#**************************************************************************************************
# Main - test
#
# Test the functionality above
#
#**************************************************************************************************

firstname = "Alex"
lastname = "Ellison"
success = getTimes(firstname, lastname)
clubID = 1
if(success):
    print("data retrieved successfully")
else:
    if(getTimes_club(firstname, lastname, clubID)):
        print("Woohoo it worked")
    else:
        print("nope it be broked")
exit