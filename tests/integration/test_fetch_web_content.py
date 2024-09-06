import unittest

from online_research_engine.fetch_web_content import WebContentFetcher


class TestWebContentFetcher(unittest.TestCase):
    def test_serper_client(self):
        services = [WebContentFetcher.SearchServices.SERPER]
        fetcher = WebContentFetcher(
            "What happened to Silicon Valley Bank", search_services=services
        )
        contents, services_response = fetcher.fetch()

        print(services_response)
        print(contents, "\n\n")

    def test_bing_web_search_client(self):
        services = [WebContentFetcher.SearchServices.BING_WEB_SEARCH]
        fetcher = WebContentFetcher(
            "What happened to Silicon Valley Bank", search_services=services
        )
        contents, services_response = fetcher.fetch()

        print(services_response)
        print(contents, "\n\n")

    def test_bing_news_search_client(self):
        services = [WebContentFetcher.SearchServices.BING_NEWS_SEARCH]
        fetcher = WebContentFetcher(
            "What happened to Silicon Valley Bank", search_services=services
        )
        contents, services_response = fetcher.fetch()

        print(services_response)
        print(contents, "\n\n")


if __name__ == "__main__":
    unittest.main()
