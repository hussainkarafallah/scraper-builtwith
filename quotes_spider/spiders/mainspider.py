# -*- coding: utf-8 -*-
import scrapy
import logging
import json
import datetime
import os
from scrapy import shell
import time

from ..items import metaItem,techItem,techinfoItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from scrapy.utils.response import open_in_browser

from scrapy import Request

mylogger = logging.getLogger("mainspider_logger")
mylogger.setLevel(logging.INFO)

fname = "./mainlog.txt"
print(fname)

fhandler = logging.FileHandler(fname, mode='w')
mylogger.addHandler(fhandler)


class MainSpider(scrapy.Spider):
    name = 'MainSpider'



    def __init__(self, mode , param , *args, **kwargs):
        super(MainSpider, self).__init__(*args , **kwargs)

        mainURL = "https://builtwith.com/"

        with open('config.json') as f:
            self.config = json.load(f)

        self.complete_login()
        self.load_cookies()

        self.meta_urls = []
        self.main_urls = []
        self.websites = []

        if mode == "w":
            websites = [param]
        else:
            with open("./" + param) as f:
                websites = f.readlines()
                websites = [x.strip() for x in websites]

        for site in websites:
            self.meta_urls.append(mainURL + "meta/" + site)
            self.main_urls.append(mainURL + site)
            self.websites.append(site)


    def start_requests(self):

        for website,url in zip(self.websites , self.meta_urls):
            yield Request(url , callback=self.parse_meta,cookies=self.cookies,cb_kwargs=dict(site = website))
        for website,url in zip(self.websites , self.main_urls):
            yield Request(url , callback=self.parse_main,cb_kwargs=dict(site = website))

    def parse_main(self , response , site):

        boxes = response.xpath('.//a[text()="View Global Trends"]/../../..')

        totaltechs = 0
        for box in boxes:
            tag = box.xpath('.//h6[@class="card-title"]/text()').extract_first()
            techs = box.xpath('.//*[@class="col-12"]/h2/a')
            totaltechs += len(techs)

            for tech in techs:

                techurl = tech.xpath('./@href').extract_first()
                techname = tech.xpath('./text()').extract_first()
                item = techItem()
                item['site'] = site
                item['domain'] = tag
                item['tech'] = techname
                yield item
                yield Request(techurl, callback=self.parse_techurl, cb_kwargs=dict(tech=techname))

        mylogger.info("Parsed website {} , techs total {}".format(site , totaltechs))

        #mylogger.info("Parsed techs for {}".format(site))

        #mylogger.info(len(hooks))

    def parse_techurl(self , response , tech):


        descxpath = '/html/body/form/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/p[@class="mb-1 small"]/text()'
        techurlxpath = '/html/body/form/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/p[@class="xsmall mb-2"]/a/@href'

        desc = response.xpath(descxpath).extract_first()
        techurl = response.xpath(techurlxpath).extract_first()

        item = techinfoItem()
        item['tech'] = tech
        item['site'] = techurl
        item['desc'] = desc

        yield item


    def parse_meta(self , response , site):
        spent = response.xpath('.//*[@class="font-weight-bold mt-3"]/text()').extract_first()
        mylogger.info("parsed meta for website {}".format(site))
        item = metaItem()
        item['site'] = site
        item['spent'] = spent
        yield item

    def complete_login(self):
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        # chrome_options.add_argument("--headless")

        user_email = self.config['EMAIL'] #kingslayer1988@gmail.com'
        user_password = self.config['PASSWORD'] #123456'
        PATH = self.config['DRIVER_PATH'] # C:\\Program Files (x86)\\chromedriver.exe'
        headless = self.config['HEADLESS']

        mylogger.info(user_email)
        mylogger.info(user_password)
        mylogger.info(PATH)


        driver = webdriver.Chrome(PATH, options=chrome_options)

        driver.get("http://builtwith.com/")

        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "Log In"))

            )
        except NoSuchElementException:
            mylogger.info("couldn't open main page")
            return

        logged_in = False
        mylogger.info("Logged In status: {}".format(logged_in))

        element.click()

        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "email"))
            )
        except NoSuchElementException:
            mylogger.info("couldn't open login form")
            return

        email = driver.find_element_by_id("email")
        email.clear()
        email.send_keys(user_email)

        password = driver.find_element_by_id("password")
        password.clear()
        password.send_keys(user_password)

        login_button = driver.find_element_by_id("main_main_btnLogin")
        time.sleep(2)
        login_button.click()
        time.sleep(5)

        cookies = driver.get_cookies()  # Selenium provides us with get_cookies to get login cookies
        driver.close()  # Get cookies to close the browser
        # Then the key is to save the cookies, after requesting to read the cookies from the file, you can save the login every time.
        # Of course, you can return the cookies back, but each subsequent request must be executed once. Login does not play the role of cookies.
        jsonCookies = json.dumps(cookies)  # Write cookies to the file via json
        with open('sel_cookies.json', 'w') as f:
            f.write(jsonCookies)
        mylogger.info(cookies)

    def load_cookies(self):
        with open('sel_cookies.json', 'r', encoding='utf-8') as f:
            listcookies = json.loads(f.read())  # Get cookies

        cookies_dict = dict()
        for cookie in listcookies:
            cookies_dict[cookie['name']] = cookie['value']
        self.cookies = cookies_dict