import unittest

from online_research_engine.web_scraper import WebScraper


class TestWebScraper(unittest.TestCase):
    def test_web_scraper(self):
        scraper = WebScraper(user_agent="macOS")
        test_url = "https://en.wikipedia.org/wiki/Apple_Inc."
        main_content = scraper.scrape_url(test_url)
        print(main_content)


if __name__ == "__main__":
    unittest.main()
