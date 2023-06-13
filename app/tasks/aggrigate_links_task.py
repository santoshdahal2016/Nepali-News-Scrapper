from config import celery_app
from app.utils.scrapers import scrape


urls = [
    "https://www.onlinekhabar.com",
    "https://ekantipur.com"
]


@celery_app.task()
def aggrigate_links_task():

    page_source = scrape("")
    print("Running aggrigate links task")