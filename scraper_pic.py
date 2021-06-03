import selenium
from selenium import webdriver
import os
import time
import requests
import io
import PIL
from PIL import Image
import hashlib
import re
import base64


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    search_url = "https://www.google.com/search?q={q}&source=lnms&tbm=isch"
    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        for _ in range(10):
            scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        for img in thumbnail_results[results_start:number_results]:

            if img.get_attribute('src') and 'http' in img.get_attribute('src'):
                image_urls.add(img.get_attribute('src'))

            if img.get_attribute('src') and 'data' in img.get_attribute('src'):
                image_urls.add(img.get_attribute('src'))

            image_count = len(image_urls)

        if len(image_urls) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)} image links, done!")
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            # return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")
                time.sleep(3)
            
            # end_of_page = wd.find_element_by_xpath("//div[@class='OuJzKb Yu2Dnd']")
            end_of_page = wd.find_elements_by_xpath("//*[ contains (text(), 'Looks like') ]")
            if end_of_page:
                print("end of the page")
                break

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def fetch_image_unsplash(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=3):
    def scroll_to_end(wd, scroll_point):  
        wd.execute_script(f"window.scrollTo(0, {scroll_point});")
        time.sleep(sleep_between_interactions)    
 
        
    # build the unsplash query
    search_url = f"https://unsplash.com/s/photos/{query}"
# load the page
    wd.get(search_url)
    time.sleep(sleep_between_interactions)  
    
    image_urls = set()
    image_count = 0
    number_results = 0
    
    for i in range(1,20):
        scroll_to_end(wd, i*1000)
        time.sleep(5)
        thumb = wd.find_elements_by_css_selector("img._2UpQX")
        time.sleep(5)
        for img in thumb:
            image_urls.add(img.get_attribute('src'))
            image_count = len(image_urls)
            number_results = image_count
            time.sleep(.5)
        print(f"Found: {number_results} search results. Extracting links...")
    return image_urls


def persist_image(folder_path:str,url:str):
    try:
        image_content = requests.get(url).content
    except requests.exceptions.InvalidSchema:
        # image is probably base64 encoded
        image_data = re.sub('^data:image/.+;base64,', '', url)
        image_content = base64.b64decode(image_data)
    except Exception as e:
        print("could not read", e, url)
        return False

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        size = (256, 256)
        resized = image.resize(size)
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
            resized.save(f, "JPEG", quality=85)
        # print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term:str,driver_path:str,target_path='./images',number_images=5):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_unsplash(search_term, number_images, wd=wd, sleep_between_interactions=1)
        # res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=1)
        
    for elem in res:
        persist_image(target_folder,elem)

    
search_terms = ['Benz', 'Audi', 'BMW']
driver_path = '/Users/yunfan/Desktop/Scraping/chromedriver'
for search_term in search_terms:
    search_and_download(search_term=search_term, driver_path=driver_path, number_images=1000)