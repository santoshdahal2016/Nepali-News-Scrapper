from config import celery_app
from app.utils.scrapers import scrape


#add news url here
urls = [
    "https://www.onlinekhabar.com",
    "https://ekantipur.com"
]



@celery_app.task()
def aggrigate_links_task():

    for website in urls:
        page_source = scrape("")



    # TODO 
    # Loop through each website and extract links and save in database
