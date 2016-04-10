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


dir = normpath(join(dirname(realpath(__file__)), "..", "save"))
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

    #extract all the dates 
    issues = driver.find_elements_by_xpath('/html/body/main/div/section/section/article[*]/div[1]/a')
    dates  = [issues[i].text for i in range(len(issues))]

    # click on each date
    for i in range(1,len(issues)+1):
        
        # have to do this again because references get stale
        issue = driver.find_element_by_xpath('/html/body/main/div/section/section/article[' + str(i) + ']/div[1]/a')
        issue.click()
        
        # iterate over all the articles and yank their info
        papers = driver.find_elements_by_xpath('/html/body/main/div/section/section[3]/article[*]')
        for p in range(2,len(papers)+1): 
            print p
            details = []  #something we'll fill up later                     
            paper_xpath = '/html/body/main/div/section/section[3]/article[' + str(p) + ']/h3/a'
            
            try:
                element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, paper_xpath)))
            except:
                break
            
            #click the paper link
            driver.find_element_by_xpath(paper_xpath).click()
        
            #yank the elements we're intersted in
            title = driver.find_element_by_xpath('/html/body/main/div/section/h1').text
            author = driver.find_element_by_xpath('/html/body/main/div/section/ul/li').text
            try: 
                keywords = driver.find_element_by_xpath('//*[@id="article-information"]/section[4]/ul').text
            except:
                keywords = driver.find_element_by_xpath('//*[@id="article-information"]/section[3]/ul').text


            date = dates[i - 1]

            #remove any ascii shit that comes up
            title = title.encode('ascii', 'ignore')
            author = author.encode('ascii', 'ignore')
            keywords = keywords.encode('ascii', 'ignore')
            date = date.encode('ascii', 'ignore')

            #add this to details array; write array to csv file
            details.append(title)
            details.append(author)
            details.append(keywords)
            details.append(date)
        
            spamwriter.writerow(details)

            # return to issue page
            driver.back()
            
        # return to issues listing
        driver.back()

driver.quit()
csvfile.close()
			
print "all done!"

