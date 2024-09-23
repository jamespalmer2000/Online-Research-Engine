import unittest

from online_research_engine.search_services import (
    BingNewsSearchClient,
    BingWebSearchClient,
    SerperClient,
    SerperPlacesClient,
)


class TestSearchClients(unittest.TestCase):
    def test_serper_client(self):
        client = SerperClient()
        query = "What happened to Silicon Valley Bank"
        response = client.serper(query)
        components = client.extract_components(response)
        print(components)

    def test_bing_web_search_client(self):
        client = BingWebSearchClient()
        query = "What happened to Silicon Valley Bank"
        response = client.bing_web_search(query)
        components = client.extract_components(response)
        print(components)

    def test_bing_news_search_client(self):
        client = BingNewsSearchClient()
        query = "What happened to Silicon Valley Bank"
        response = client.bing_news_search(query)
        components = client.extract_components(response)
        print(components)

    def test_serper_places_client(self):
        client = SerperPlacesClient()
        query = "Bobcat Company"
        location = "58078, North Dakota, United States"
        country = "us"
        response = client.serper_places_search(
            query, location=location, country=country
        )
        components = client.extract_components(response)
        print(components)


if __name__ == "__main__":
    unittest.main()
