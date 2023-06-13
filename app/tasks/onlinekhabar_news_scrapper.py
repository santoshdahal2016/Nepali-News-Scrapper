from config import celery_app


# This job is called by the signal of link model 
# and can also called if failed due system issue 

@celery_app.task()
def onlinekhabar_news_scrapper(link_id):


    # Get link detail through link id 
    # Detect if the url needs to scrapped if not update it to invalid urls
    # if yes Scrape it  
    # Update row with title , date , body(text) and page_source of link if sucess 
    pass