import argparse
import concurrent
import logging
import os
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm.auto import tqdm


def setup_driver(headless=True):
    """
    Setup a WebDriver used for selenium, using --headeless option as default
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_element(driver, by_method, value, timeout=10, retry_interval=5, max_retries=3):
    """
    """
    retries = 0
    while retries < max_retries:
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by_method, value)))
        except TimeoutException:
            print(f"Retry {retries+1}/{max_retries} for element {value} after timeout.")
            time.sleep(retry_interval)
            retries += 1
        finally:
            print(f"Retry {retries+1}/{max_retries} for element {value} after timeout.")
            time.sleep(retry_interval)
    # raise TimeoutException(f"Element {value} not found after {max_retries} retries.")
    return "Missing Value or Timeout"  # Return None if element is not found

def fetch_data(collection_id):
    driver = setup_driver()
    try:
        print(f"Fetching data for collection: {collection_id}\n.")
        driver.get(f"https://www.cvh.ac.cn/spms/detail.php?id={collection_id}")
        
        # Fetch specific details as per your logic
        data = {
            'Collection ID': collection_id,
            'Image Link': wait_for_element(driver, By.ID, "spm_image", max_retries=5).get_attribute('src'),
            'Phylum (门)': wait_for_element(driver, By.ID, "taxon_phy_c", max_retries=5).text,
            'Order (目)': wait_for_element(driver, By.ID, "taxon_ord_c", max_retries=5).text,
            'Family (科)': wait_for_element(driver, By.ID, "taxon_fam_c", max_retries=5).text,
            'Genus (属)': wait_for_element(driver, By.ID, "taxon_gen_c", max_retries=5).text,
            'Scientific Name': wait_for_element(driver, By.ID, "formattedName", max_retries=5).text,
            'Chinese Name': wait_for_element(driver, By.ID, "chineseName", max_retries=5).text,
            'Identified By': wait_for_element(driver, By.ID, "identifiedBy", max_retries=5).text,
            'Date Identified': wait_for_element(driver, By.ID, "dateIdentified", max_retries=5).text,
            'Collector': wait_for_element(driver, By.ID, "recordedBy", max_retries=5).text,
            'Collection Number': wait_for_element(driver, By.ID, "recordNumber", max_retries=5).text,
            'Collection Date': wait_for_element(driver, By.ID, "verbatimEventDate", max_retries=5).text,
            'Collection Location': wait_for_element(driver, By.ID, "locality", max_retries=5).text,
            'Altitude': wait_for_element(driver, By.ID, "elevation", max_retries=5).text,
            'Habitat': wait_for_element(driver, By.ID, "habitat", max_retries=5).text,
            'Phenology': wait_for_element(driver, By.ID, "reproductiveCondition", max_retries=5).text
        }
        return data
    finally:
        driver.quit()

def fetch_collection_data_concurrently(collection_ids, max_workers=5):
    results = []
    
    # Initialize an empty DataFrame to hold column names. This is useful if you expect your first few calls might fail and return None.
    temp_path = "./scraper_results/temp_results.csv"
    pd.DataFrame(columns=['Collection ID', 'Image Link', 'Phylum (门)', 'Order (目)', 'Family (科)', 
                          'Genus (属)', 'Scientific Name', 'Chinese Name', 'Identified By', 
                          'Date Identified', 'Collector', 'Collection Number', 'Collection Date', 
                          'Collection Location', 'Altitude', 'Habitat', 'Phenology']).to_csv(temp_path, mode='w', index=False, encoding='utf-8-sig')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_data, cid) for cid in collection_ids]
        for future in tqdm(as_completed(futures), total=len(collection_ids)):
            results.append(future.result())
            result = future.result()
            if result:
                # Append the result to the CSV file
                try:
                    pd.DataFrame([result]).to_csv(temp_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                except PermissionError:
                    continue

    df = pd.DataFrame(results)
    return df

def main():
    """Main function to orchestrate the web scraping process."""
    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # URL to scrape
    url = "https://www.cvh.ac.cn/spms/list.php?&offset=0"

    # Open the URL
    driver.get(url)

    # Wait for the dynamic content to load
    time.sleep(5)  # Adjust the sleep time according to your internet speed and website response

    # Find all elements with the specified class
    rows = driver.find_elements(By.CLASS_NAME, 'spms-row')

    # Extract data-collection-id from each row
    data_collection_ids = [row.get_attribute('data-collection-id') for row in rows]

    # Close the WebDriver
    driver.quit()

    # Create a DataFrame
    data_collection_ids  = pd.DataFrame(data_collection_ids, columns=['Data Collection ID'])

    # Save results
    sample_collections = list(data_collection_ids['Data Collection ID'])
    results = fetch_collection_data_concurrently(sample_collections, 30) 
    results_path = "./scraper_results/results.csv"
    results.to_csv(results_path, header=True, index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web Scraper for CVH Data')
    parser.add_argument('--output_dir', required=True, help='Directory to save the scraping results.')
    parser.add_argument('--offset', required=False, help='Offset to the CVH website.')
    args = parser.parse_args()

    main(args.collection_ids_path, args.output_dir)
