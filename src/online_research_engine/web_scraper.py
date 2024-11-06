import re

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class WebScraper:
    def __init__(self, user_agent="macOS"):
        # Initialize the scraper with a user agent (default is 'macOS')
        self.headers = self._get_headers(user_agent)

    def _get_headers(self, user_agent):
        # Private method to get headers for the request based on the specified user agent
        if user_agent == "macOS":
            # Headers for macOS user agent
            return {
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            }
        else:
            # Headers for Windows user agent
            return {
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            }

    def get_webpage_html(self, url):
        # Fetch the HTML content of a webpage from a given URL
        response = requests.Response()  # Create an empty Response object
        if url.endswith(".pdf"):
            # Skip PDF files which are time consuming
            return response

        try:
            # Attempt to get the webpage content with specified headers and timeout
            response = requests.get(url, headers=self.headers, timeout=8)
            response.encoding = "utf-8"
        except requests.exceptions.Timeout:
            # Add timeout exception handling here
            return response

        return response

    def convert_html_to_soup(self, html):
        # Convert the HTML string to a BeautifulSoup object for parsing
        html_string = html.text
        return BeautifulSoup(html_string, "lxml")

    def extract_main_content(self, html_soup, rule=0):
        # Extract the main content from a BeautifulSoup object
        main_content = []
        tag_rule = re.compile("^(h[1-6]|p|div)" if rule == 1 else "^(h[1-6]|p)")
        # Iterate through specified tags and collect their text
        for tag in html_soup.find_all(tag_rule):
            tag_text = tag.get_text().strip()
            if tag_text and len(tag_text.split()) > 10:
                main_content.append(tag_text)
        return "\n".join(main_content).strip()

    def scrape_url(self, url, rule=0):
        # Public method to scrape a URL and extract its main content
        webpage_html = self.get_webpage_html(url)
        soup = self.convert_html_to_soup(webpage_html)
        main_content = self.extract_main_content(soup, rule)
        return main_content


class PlaywrightWebScraper:
    def __init__(self):
        return

    def get_webpage_html(self, url):
        # NOTE: unlike WebScraper.get_webpage_html,
        # this function returns the response text, not the response object itself
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                response = page.goto(url)
                response.finished()
            except PlaywrightTimeoutError:
                return ""

            page_content = page.content()
            browser.close()

            return page_content

    def convert_html_to_soup(self, html):
        # Convert the HTML string to a BeautifulSoup object for parsing
        html_string = html
        return BeautifulSoup(html_string, "lxml")

    def extract_main_content(self, html_soup, rule=0):
        # Extract the main content from a BeautifulSoup object
        main_content = []
        tag_rule = re.compile("^(h[1-6]|p|div)" if rule == 1 else "^(h[1-6]|p)")
        # Iterate through specified tags and collect their text
        for tag in html_soup.find_all(tag_rule):
            tag_text = tag.get_text().strip()
            if tag_text and len(tag_text.split()) > 10:
                main_content.append(tag_text)
        return "\n".join(main_content).strip()

    def scrape_url(self, url, rule=0):
        # Public method to scrape a URL and extract its main content
        webpage_html = self.get_webpage_html(url)
        soup = self.convert_html_to_soup(webpage_html)
        main_content = self.extract_main_content(soup, rule)
        return main_content
