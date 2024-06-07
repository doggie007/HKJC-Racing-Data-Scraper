# HKJC-Racing-Data-Scraper

Tools to scrape and preprocess data for Hong Kong Jockey Club's racing data for machine learning / data visualization purposes.

## race_scraper.py

Scrapes both race information and result from https://racing.hkjc.com/racing/information/english/Racing/LocalResults.aspx. See example data in Data-Examples folder and usage in example_usage.py.

Note: 
- Only local races are scraped
- Only scrapes races where the top-left corner displays "Class x", likely missing out on Group 1 races and other special event races


## data_handler.py
Currently in development

## horse_scraper.py
Currently in development.