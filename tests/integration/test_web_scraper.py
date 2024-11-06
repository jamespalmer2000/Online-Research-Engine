import unittest

from online_research_engine.web_scraper import PlaywrightWebScraper, WebScraper


class TestWebScraper(unittest.TestCase):
    def test_web_scraper(self):
        scraper = WebScraper(user_agent="macOS")
        test_url = "https://en.wikipedia.org/wiki/Apple_Inc."
        main_content = scraper.scrape_url(test_url)
        print(main_content)


class TestPlaywrightWebScraper(unittest.TestCase):
    def test_get_webpage_html(self):
        scraper = PlaywrightWebScraper()
        test_url = "https://www.apple.com"
        webpage_html = scraper.get_webpage_html(test_url)
        print(webpage_html)

    def test_web_scraper(self):
        scraper = PlaywrightWebScraper()
        test_url = "https://www.apple.com"
        main_content = scraper.scrape_url(test_url, rule=1)
        print(main_content)


if __name__ == "__main__":
    unittest.main()
