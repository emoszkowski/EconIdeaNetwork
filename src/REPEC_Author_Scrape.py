#import your shit
from selenium import webdriver  #the all-important webdriver module
from bs4 import BeautifulSoup #nice little HTML parser; don't use regex
import sys, csv #I like these things
import os

#added functionality for webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.chdir(u'C:\\Users\\ganstrei\\Desktop') #or wherever you want the CSV file stored

#name our csv file and open it
repec_csv_file = "REPEC_Paper_Info.csv"

with open(repec_csv_file, 'wb') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(['Institution', 'Author'])

    # set up driver
    driver = webdriver.Chrome()
    
    #i don't do your fancy shit; we do this caveman style!
    for i in range (1, 51):
        driver.get('https://edirc.repec.org/usa-top.html')

        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "main")))

        #get the school name
        school_name = driver.find_element_by_xpath('//*[@id="main"]/dl/dt['+str(i)+']').text

        #click the school linsk
        driver.find_element_by_xpath('//*[@id="main"]/dl/dd['+str(i)+']/ul/li/a').click()

        #varying numbers of lists on these pages; we want the 2nd to last
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        lists = soup.find_all('ol')    
        listnum = len(lists) - 1

        #now we're on the school page; grab all the affiliations and high tail it out
        for j in range(1, 101):
            try:
                author = driver.find_element_by_xpath('//*[@id="main"]/ol['+str(listnum)+']/li['+str(j)+']/a').text
                details = [school_name, author]
                spamwriter.writerow(details)
            except:
                continue
    driver.quit()
    csvfile.close()
print "all done!"