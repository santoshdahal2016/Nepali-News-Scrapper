
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def scrape(url):

    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Remote(
        command_executor='http://localhost:4444',
        options=firefox_options
    )
    
    driver.get(url)

    page_source = driver.execute_script("return document.body.innerHTML;")
    driver.quit() 

    return page_source 

print(scrape("https://www.onlinekhabar.com"))
