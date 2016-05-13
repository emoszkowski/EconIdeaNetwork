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
import numpy as np

def _match(x):
    return (x[0] == 'w') or (x[0] == 't')

#name our csv file and open it
path = '../save/'
nber_csv_file = "NBER_Paper_Info.csv"

# set up driver
driver = webdriver.Chrome()
driver.get('http://nber.org/jel/')

element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "mainContentTd")))

# Get list of JEL codes
codes = driver.find_elements_by_xpath('/html/body/div/table/tbody/tr/td/ul/a[*]')
nCodes = len(codes)

dfs = []

for currCode in range(1, nCodes+1):

    print codes[currCode-1]

    codelink = driver.find_element_by_xpath('/html/body/div/table/tbody/tr/td/ul/a[' + \
                                         str(currCode) + ']')
    codelink.click()

    # Get Minor JEL Classes

    minorClasses = driver.find_elements_by_xpath('//*[@id="mainContentTd"]/ul/li[*]') 
    nMinorClasses = len(minorClasses)

    for currMinorClass in range(1, nMinorClasses+1):

        print minorClasses[currMinorClass-1]

        # Go to page with papers for a single minor JEL class
        classlink = driver.find_element_by_xpath('//*[@id="mainContentTd"]/ul/li[' + str(currMinorClass) + ']')
        classCode = classlink.text.split(' ')[0][1:-1]
        
        driver.get('http://nber.org/jel/' + classCode + '.html')

        # Get List of Papers
        papers = driver.find_elements_by_xpath('//*[@id="mainContentTd"]/table/tbody/tr[*]')

        # format papers + years
        papersDf = pd.DataFrame([p.text for p in papers])

        # Extract years and fill forward to assign
        # year to each paper
        papersDf['year'] = papersDf[0]
        papersDf.year[papersDf.year.apply(_match)] = np.nan
        papersDf.year = papersDf.year.ffill()
        papersDf = papersDf[papersDf[0].apply(_match)]

        # Split text into authors & titles
        papersDf[0] = papersDf[0].apply(lambda x: x.split(' ',1)[1].split('\n'))
        papersDf['authors'] = papersDf[0].apply(lambda x: x[0:-1])
        papersDf['title'] = papersDf[0].apply(lambda x: x[-1])

        # Add in JEL codes and cleanup
        papersDf['jel'] = classCode
        del papersDf[0]

        dfs.append(papersDf)
        driver.back()
        
    driver.back()
 
dfs = pd.concat(dfs)

# Collapse Duplicates into single entry
# with all JEL codes

jels = dfs.groupby('title').jel.unique().reset_index()
authors = dfs.groupby('title').first().reset_index()
del authors['jel']

dfsFinal = pd.merge(authors, jels, how='outer', on='title')

# Format authors/jel strings
dfsFinal.authors = dfsFinal.authors.apply(lambda x: ', '.join(x))
dfsFinal.jel = dfsFinal.jel.apply(lambda x: ', '.join(x))

# Encode to ASCII
dfsFinal.title = dfsFinal.title.apply(lambda x: x.encode('ascii','ignore'))
dfsFinal.authors = dfsFinal.authors.apply(lambda x: x.encode('ascii','ignore'))
dfsFinal.jel = dfsFinal.jel.apply(lambda x: x.encode('ascii','ignore'))
dfsFinal.year = dfsFinal.year.apply(lambda x: x.encode('ascii','ignore'))

# Write to File
dfsFinal.to_csv(path + nber_csv_file, sep='|')
