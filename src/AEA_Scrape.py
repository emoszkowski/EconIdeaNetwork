#import your shit
from selenium import webdriver  #the all-important webdriver module
from bs4 import BeautifulSoup #nice little HTML parser; don't use regex
import sys, csv #I like these things
from os.path import *
import os

#added functionality for webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

dir = normpath(join(dirname(realpath('')), ".", "save"))
os.chdir(dir) #or wherever you want the CSV file stored

#name our csv file and open it
aea_csv_file = "AEA_Paper_Info.csv"

with open(aea_csv_file, 'wb') as csvfile:

    #initialize our CSV writer and write our first row
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(["Paper Name", "Paper Author", "Paper Key Words", "Issue Date"])

    driver = webdriver.Chrome()
    driver.get('https://www.aeaweb.org/aer/issues.php')

    # wait to make sure that the element is clickable -- selenium can be hasty sometime
    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "main-content")))

    # get list of volumes
    volumes = driver.find_elements_by_xpath('/html/body/main/div/section/section/article[*]')
    nVolumes = len(volumes)

    # click on each volume
    for currVolume in range(0,nVolumes):

        # get list of dates
        dates = driver.find_elements_by_xpath('/html/body/main/div/section/section/article[' + \
                                              str(currVolume) + ']/div[*]/a')
        dates = [d.text for d in dates]
        nDates = len(dates)

        # click on each issue
        for currDate in range(1,nDates+1):

            # Load Date String
            datestr = dates[currDate - 1]
            
            # Skip if May edition (historically, the P&P issue)
            if 'May' in datestr:
                continue

            # have to do this again because references get stale
            # if no currDateth issue, move to next Volume

            issue = driver.find_element_by_xpath('/html/body/main/div/section/section/article[' + \
                                                 str(currVolume) + ']/div[' + \
                                                 str(currDate) + ']/a')
            issue.click()
            
            # iterate over all the articles and yank their info
            papers = driver.find_elements_by_xpath('/html/body/main/div/section/section[contains(@class,"journal-article-group")]/article[*]')
            for p in range(2,len(papers)+1): 

                print str(currVolume) + '\t' + str(currDate) + '\t' + str(p) + '\n'
                details = []  #something we'll fill up later                     

                # Click on Paper Link
                paper_xpath = '/html/body/main/div/section/section[contains(@class,"journal-article-group")]/article[' + str(p) + ']/h3/a'
                try:
                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, paper_xpath)))
                    driver.find_element_by_xpath(paper_xpath).click()
                except:
                    continue

                try:

                    # Grab Title
                    title = driver.find_element_by_xpath('/html/body/main/div/section/h1').text

                    # Grab Author(s)
                    authors = driver.find_elements_by_xpath('/html/body/main/div/section/ul/li[contains(@class,"author")]')
                    authors = ';'.join([a.text for a in authors])

                    # Grab JEL Classification(s)
                    keywords = driver.find_element_by_xpath('//*[@id="article-information"]/section[contains(@class,"jel-classification")]/ul').text
                    keywords = keywords.replace('\n',';')

                    #remove any ascii shit that comes up
                    title = title.encode('ascii', 'ignore')
                    authors = authors.encode('ascii', 'ignore')
                    keywords = keywords.encode('ascii', 'ignore')
                    datestr = datestr.encode('ascii', 'ignore')

                    #add this to details array; write array to csv file
                    details.append(title)
                    details.append(authors)
                    details.append(keywords)
                    details.append(datestr)

                    spamwriter.writerow(details)
                    driver.back()

                except:
                    # Grabbing Title, Author, or JEL Codes failed

                    # return to issue page
                    driver.back()
                    continue

            # return to issues listing
            driver.back()

driver.quit()
csvfile.close()
			
print "all done!"

