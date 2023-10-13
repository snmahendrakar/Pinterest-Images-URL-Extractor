from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import threading


# Function to scroll through the page
def scroll_page(driver, num_urls_to_print, sleep_time):
    image_urls = set()
    
    while True:
        prev_len = len(image_urls)
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(1, document.body.scrollHeight)")
        time.sleep(sleep_time)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract new image URLs
        new_image_urls = extract_image_urls(soup, num_urls_to_print - len(image_urls), image_urls)
        image_urls.update(new_image_urls)
        
        # Check if No Pins are found for the tag
        if "We couldn't find any Pins for" in soup.text:
            print("Sorry! No pins were found for the tag")
            break
        
        # Check if scroll has reached the end
        if len(image_urls) == prev_len:
            print("We've reached the end of search results")
            break

    return image_urls


# Function to extract image URLs from the page
def extract_image_urls(soup, max_urls, existing_urls):
    new_image_urls = set()
    for link in soup.find_all('img'):
        image_url = link.get('src')
        if image_url and image_url not in existing_urls and len(new_image_urls) < max_urls:
            new_image_urls.add(image_url)
            #print(image_url, end= '\n')
    return new_image_urls

# Function to save obtained image URLs to a CSV file
def save_urls_to_csv(image_urls, tag):
    csv_filename = tag + "_urls_" + str(time.time()) + ".csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Image URLs"])
        for url in image_urls:
            csv_writer.writerow([url])
    print(f"{len(image_urls)} Image URLs saved to {csv_filename}")


# Function that runs all the tags at the same time to make the code more efficient
def initiator(tag, num_urls_to_print):
    sleep_time = 2
    url = "https://in.pinterest.com/search/pins/?q=" + tag
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    image_urls = scroll_page(driver, num_urls_to_print, sleep_time)

    driver.quit()

    if len(image_urls) > 0:
        save_urls_to_csv(image_urls, tag)


def main():

    # Get input tags separated by commas
    var = input("Enter the tags to be searched (separated by commas): ").split(',')
    
    num_urls_to_print = int(input("Enter the number of URLs to fetched: "))

    #Threading used to run the tasks simultaneously
    for tag in var:
        threading.Thread(target=initiator,args=(tag,num_urls_to_print)).start()
        

if __name__ == "__main__":
    main()
