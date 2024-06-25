from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FX():

    def __init__(self):
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument("start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-dev-shm-usage")

        self.links = []
        self.article_list = []
        self.driver = webdriver.Chrome(options=self.options)

    def get_links(self, driver):
        articles = driver.find_elements(By.CLASS_NAME, "ais-hits--item")
        for article in articles:
            title_element = article.find_element(By.CLASS_NAME,
                                                 'fxs_headline_tiny').find_element(
                                                    By.TAG_NAME, 'a')
            link = title_element.get_attribute('href')
            self.links.append(link)
        return self.links

    def scrape_article_content(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        # find and extract the title, date, and content
        title_tag = soup.find('h1', {'class': "fxs_headline_tiny"})
        title = title_tag.text.strip() if title_tag else 'No title found'
        date_tag = soup.find('time')
        if date_tag:
            date_str = date_tag.text
            try:
                # convert the string to a datetime object
                date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S %Z')
                date = date_obj.strftime('%B %d, %Y')
            except ValueError:
                date = 'Date format error'
        else:
            date = 'No date found'
        article_div = soup.find('div', {'class': 'fxs_article_content'})
        article_text = article_div.text.strip() if article_div else 'No article text found'
        return {'date': date, 'title': title, 'body': article_text}

    def scrape_articles(self):
        try:
            url = "https://www.fxstreet.com/news/latest/asset?dFR[Category][0]=News&dFR[Tags][0]=XAUUSD"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 30)
            self.get_links(self.driver)  # Scrape first page

            for page_num in range(1, 2):
                print(f"looking for 'NEXT' link on page {page_num}")
                wait = WebDriverWait(self.driver, 10)
                next_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.ais-pagination--link[aria-label="Next"]')))
                next_page_href = next_link.get_attribute('href')  # Get the href attribute for navigation
                print(f"next page href: {next_page_href}")
                self.driver.get(next_page_href)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'fxs_clearfix')))
                self.get_links(self.driver)
                print(f"finished scraping page {page_num}")

            for link in self.links:
                article = self.scrape_article_content(link)
                self.article_list.append(article)

        except Exception as e:
            print(f"Error scraping main page: {e}")
        finally:
            self.driver.quit()

        return pd.DataFrame(self.article_list)

# Example usage:
if __name__ == "__main__":
    scraper = FX()
    articles_df = scraper.scrape_articles()
    articles_df.to_csv("FX.csv")
    print(articles_df)