
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from environs import Env


env = Env()
env.read_env()

def scrape(url):

    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Remote(
        command_executor=env("SELENIUM_HOST"),
        options=firefox_options
    )
    
    driver.get(url)

    page_source = driver.execute_script("return document.body.innerHTML;")
    driver.quit() 

    return page_source 

