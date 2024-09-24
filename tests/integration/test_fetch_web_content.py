import unittest

from online_research_engine.fetch_web_content import (
    PlacesContentFetcher,
    WebContentFetcher,
)


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


class TestPlacesContentFetcher(unittest.TestCase):
    def test_serper_places_client(self):
        fetcher = PlacesContentFetcher(
            "S & S Landscaping",
            search_args={"location": "58103, North Dakota, United States"},
        )
        contents, services_response = fetcher.fetch()


if __name__ == "__main__":
    unittest.main()
