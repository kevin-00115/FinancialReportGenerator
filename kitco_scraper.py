import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Scraper():
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument("start-maximized"); 
        self.options.add_argument("disable-infobars"); 
        self.options.add_argument("--disable-extensions"); 
        self.options.add_argument("--disable-gpu"); 
        self.options.add_argument("--disable-dev-shm-usage"); 

        self.article_list = []

    def get_links(self, driver):
        articles = driver.find_elements(By.CLASS_NAME, "DigestNews_newItem__K4a83")
        return [element.find_element(By.TAG_NAME, 'a').get_attribute('href') for element in articles]

    def scrape_article_content(self, driver, link):
        driver.get(link)
        time.sleep(5)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('h1', {'class': "mb-6 !font-lato text-[34px] font-bold leading-[39px]"})
        title = title_tag.text if title_tag else 'No title found'
        article_div = soup.find('div', {'class': 'relative text-base article-alias_articleBodyStyles__zkPMo article-alias_articleWrapper__atgO6', 'id': 'articleBody'})
        paragraphs = article_div.find_all('p') if article_div else []
        article_text = '\n'.join(p.text for p in paragraphs)
        date_time_tag = soup.find('time')
        date_time_str = date_time_tag.text.strip() if date_time_tag else 'No date found'
        date_regex = r"\b\w{3} \d{1,2}, \d{4}\b"
        match = re.search(date_regex, date_time_str)
        date = match.group(0) if match else 'Date format error'
        return {'date': date, 'title': title, 'body': article_text}

    def scrape_articles(self):
        driver = webdriver.Chrome(options=self.options)
        driver.set_page_load_timeout(60)
        try:
            url = "https://www.kitco.com/news/digest#metals"
            driver.get(url)
            load_more_button = driver.find_element(By.CLASS_NAME, "py-3")
            for _ in range(2):
                load_more_button.click()
                time.sleep(5)
            links = self.get_links(driver)
            
            for link in links:
                try:
                    article = self.scrape_article_content(driver, link)
                    self.article_list.append(article)
                except Exception as e:
                    print(f"Error processing link {link}: {e}")
        except Exception as e:
            print(f"Error scraping main page: {e}")
        finally:
            driver.quit()
        return pd.DataFrame(self.article_list)

# Example usage:
if __name__ == "__main__":
    scraper = Scraper()
    articles_df = scraper.scrape_articles()
    articles_df.to_csv("articles.csv")
    print(articles_df)

