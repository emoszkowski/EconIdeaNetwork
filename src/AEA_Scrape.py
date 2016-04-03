#import your shit
from selenium import webdriver  #the all-important webdriver module
from bs4 import BeautifulSoup #nice little HTML parser; don't use regex
import os, csv #I like these things

#added functionality for webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#desktop = u'C:\\Users\\ganstrei\\Desktop'
desktop = u'/Users/ericamoszkowski/Documents/NYU/SocialNetworks/EconIdeaNetwork/save/'

os.chdir(desktop) #or wherever you want the CSV file stored

#I don't think you have to do this if you install chromedriver with brew, but 
#I'm programming on a windows machine, which sucks.
# path_to_chromedriver = u'C:\\Users\\ganstrei\\Desktop\\chromedriver.exe'
#path_to_chromedriver = u'/Users/ericamoszkowski/Library/chromedriver.exe'

#name our csv file and open it
aea_csv_file = "AEA_Paper_Info.csv"

with open(aea_csv_file, 'wb') as csvfile:
	#initialize our CSV writer and write our first row
	spamwriter = csv.writer(csvfile)

	spamwriter.writerow(["Paper Name", "Paper Author", "Paper Key Words", "Issue Date"])

	#start our driver
	#driver = webdriver.Chrome(executable_path = path_to_chromedriver)
	driver = webdriver.Chrome()

	#navigate to where we'll start.
	driver.get('https://www.aeaweb.org/aer/issues.php')

	#inspect march 2016 element and copy its xpath.
	#should be intuitive to you regarding how you could iterate over xpaths

	#wait to make sure that the element is clickable -- selenium can be hasty sometime
	element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent3"]/p[2]/a[1]')))

	#extract date you're working with
	date = driver.find_element_by_xpath('//*[@id="mainContent3"]/p[2]/a[1]').text


	#find the element with the xpath and click it
	driver.find_element_by_xpath('//*[@id="mainContent3"]/p[2]/a[1]').click()

	#now you're on the page that has all the papers published in this issue; we have to iterate over clicking them and yanking their content


	for i in range (7, 15):
		details = []  #something we'll fill up later

		#example of xpath iteration
		paper_xpath = '//*[@id="mainContent3"]/div[' + str(i) + ']/div/a'

		try:
			element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, paper_xpath)))
		except:
			break

		#click the paper link
		driver.find_element_by_xpath(paper_xpath).click()

		#yank the elements we're intersted in

		title = driver.find_element_by_xpath('//*[@id="dialog_h2"]').text
		author = driver.find_element_by_xpath('//*[@id="resize_window"]/div[9]').text
		keywords = driver.find_element_by_xpath('//*[@id="resize_window"]/div[11]').text

		#remove any ascii shit that comes up
		title = title.encode('ascii', 'ignore')
		author = author.encode('ascii', 'ignore')
		keywords = keywords.encode('ascii', 'ignore')

		#add this to details array; write array to csv file
		details.append(title)
		details.append(author)
		details.append(keywords)
		details.append(date)

		spamwriter.writerow(details)

		driver.back()

	driver.quit()

	csvfile.close()

print "all done!"
