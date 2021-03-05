import sys
import math
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

imagesList = {}
basePath = "./keywords-list/"
keywordsPath = basePath + sys.argv[1]
imagesSavePath = "./results/" + sys.argv[1] + ".list"

cap = DesiredCapabilities().FIREFOX
options = Options()
options.headless = True
#browser = webdriver.Firefox(options=options, capabilities=cap, firefox_binary = "/usr/lib64/firefox/firefox", executable_path = "/home/lz/dockerhub-scan/geckodriver")
browser = webdriver.Firefox(options=options, capabilities=cap, executable_path = "/home/lz/dockerhub-scan/geckodriver")

class resolve_images_thread(threading.Thread):
    def __init__(self, keyword):
        global imagesList
        threading.Thread.__init__(self)
        self.keyword = keyword.strip()
        self.pages = 1
        self.flag = 0

        #options = Options()
        #options.headless = True
        #self.browser = webdriver.Firefox(options=options)

    def run(self):
        print('Start resolving images Thread: ', self.keyword)
        self.resolve_images_list()
        #self.browser.quit()

    def resolve_images_list(self):
        imagelist = ""
        index = 1
        while index <= self.pages:
            url = "https://hub.docker.com/search?q={}&type=image&page={}&page_size=50".format(self.keyword, str(index))
            for i in range(5):
                try:
                    browser.get(url)
                    break
                except Exception as e:
                    continue
                    pass

            try:
                 element = Wait(browser, 10).until(
                    Expect.presence_of_element_located((By.ID, "searchResults"))
                 )
            except Exception as e:
                 with open("./failed_keyword.list", "a+") as fail:
                    fail.write(self.keyword)

            if 'no results' in element.text:
                print ("There doesn't have search results...")
                return 0

            if self.flag == 0:
                soup = BeautifulSoup(browser.page_source,'html.parser')
                links = soup.find_all('div',class_="styles__currentSearch___35kW_")
                for link in links:
                    if "-" in link.div.text and "of" in link.div.text:
                        num = link.div.text.split()[4]
                        self.pages = check_number(num)
                        self.flag = 1

            content = element.text.split('\n')
            for index in range(len(content)):
                if 'Updated' in content[index] and 'ago' in content[index]:
                    if '/' in content[index-1] and content[index-1] not in imagesList.keys():
                        imagesList[content[index-1]] = 1
                        imagelist = imagelist + content[index-1] + "\n"

        with open(imagesSavePath, 'a+') as images_list:
            images_list.write(imagelist)

def check_number(number):
    num = str(number).split(',')
    # num over 1,000,000
    if len(num) > 2:
        return 0
    # num less 1,000
    elif len(num) == 1:
        return math.ceil(int(number)/50)

    try:
        imageNum = int(num[0]) * 1000 + int(num[1])
        if imageNum < 2500:
            return math.ceil(imageNum/50)
    except Exception as e:
        return 0

    return 0

def main():
    cores = 1
    file =  open(keywordsPath, "r+")
    lines = file.readlines()

    crawl_thread = []
    for keyword in lines:
        thread = resolve_images_thread(keyword)
        # keep the threads < cores numbers
        if len(threading.enumerate()) <= cores:
            thread.start()
            crawl_thread.append(thread)
        else:
            for t in crawl_thread:
                t.join()

    for t in crawl_thread:
        t.join()

    file.close()
    browser.quit()

if __name__ == "__main__":
    main()

