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

import pandas as pd

dir = normpath(join(dirname(realpath('')), ".", "save"))
os.chdir(dir) #or wherever you want the CSV file stored

#name our csv file and open it
repec_csv_file = "REPEC_Paper_Info.csv"

# set up driver
driver = webdriver.Chrome()
driver.get('https://edirc.repec.org/usa-top.html')

element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "main")))



# Get list of departments
departments = driver.find_elements_by_xpath('//*[@id="main"]/dl/dd[*]/ul/li/a')
nDepartments = len(departments)

dfs = []
sectionStr = u'People who have registered with RePEc and have claimed to be affiliated with this institution:'


# for each department...
for currDep in range(1, nDepartments+1):

    depName = driver.find_element_by_xpath('//*[@id="main"]/dl/dt[' + str(currDep) + ']').text
    print depName

    deplink = driver.find_element_by_xpath('//*[@id="main"]/dl/dd[' + str(currDep) + ']/ul/li/a')
    deplink.click()

    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "main")))

    # Get authors in the department
    links = driver.find_elements_by_xpath('//*[@id="main"]/h3[*]')
    sections = [link.text for link in links]

    if not sections:
        continue
    
    authorListInd = sections.index(sectionStr) + 2

    authors = driver.find_elements_by_xpath('//*[@id="main"]/ol[' + str(authorListInd) + ']/li[*]') 
    nAuthors = len(authors)
    authorNames = []

    for currAuthor in range(1, nAuthors+1):

        authorlink = driver.find_element_by_xpath('//*[@id="main"]/ol[' + str(authorListInd) + ']/li[' + str(currAuthor) + ']/a')
        authorNames.append(authorlink.text)
        print authorlink.text

    # make dataframe of authors/department
    df = pd.DataFrame([authorNames]).transpose()
    df.columns = ['author']
    df['department'] = depName
    
    # add it to dfs
    dfs.append(df)
    
    # go back to the page with all the departments
    driver.back()

dfs = pd.concat(dfs)

# Encode to ASCII
dfs.author = dfs.author.apply(lambda x: x.encode('ascii','ignore'))
dfs.department = dfs.department.apply(lambda x: x.encode('ascii','ignore'))

# Write to File
dfs.to_csv(repec_csv_file, sep='|')
