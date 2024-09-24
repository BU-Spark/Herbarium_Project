# Documentation for the scraper functionalities
@PalmPalm7

# How to use
* Please refer to /ml-herbarium/Spring2024/scraper/src/ML_Herbaria_CVH_Web_Scraper.ipynb
* The pipeline could be ran on SCC or Google Colab. It mainly used selenium for automation. Please modify path variables accordingly.

# Progress Report - May 7th, 2024
@PalmPalm7
## Progress
* Finished scraping ~30000 entities
* ~15,000 samples are clean, with no duplications and no missing field
* 1000 samples were selected for benchmark
* Have updated the script with headless to run without a physical browser. Chronium driver is still needed.

## Problem
* Need to implement failed-to-scrape logic.
* Need to handle more concurrencies
* Preferrable with dockerized container and orchestration.

## Plan
* SE the scraper code
* Capusalize it with docker.

# Progress Report - March 31st, 2024
@PalmPalm7
## Progress
* Finished implemented a webscraping pipeline for the CVH datasets
* Scraped 180 entities in first batch 
* Have set up a scraping automation pipeline with crontab and shellscript to perform the ETL process.

## Problem
* Error Handling for scraper code
* Headless option to be able to run the code on a VM
* Currently the CVH's index is meaningless, scraping from the start gives you only the a small subset.

## Plan
* SE the scraper code
* Complete headless option scraper
* Identify handwritten datasets (by year maybe?)
* Scraper more samples (10000)
* Capusalize it with docker.
