import threading
import time
from enum import Enum

from .search_services import BingNewsSearchClient, BingWebSearchClient, SerperClient
from .web_scraper import WebScraper


class WebContentFetcher:
    SearchServices = Enum(
        "SearchServices", ["SERPER", "BING_WEB_SEARCH", "BING_NEWS_SEARCH"]
    )

    def __init__(
        self,
        query,
        search_services=[SearchServices.SERPER],
        search_args={},
        config_path=None,
    ):
        # Initialize the fetcher with a search query
        self.query = query
        self.search_services = search_services
        self.search_args = search_args
        self.config_path = config_path
        self.web_contents = []  # Stores the fetched web contents
        self.error_urls = []  # Stores URLs that resulted in an error during fetching
        self.web_contents_lock = (
            threading.Lock()
        )  # Lock for thread-safe operations on web_contents
        self.error_urls_lock = (
            threading.Lock()
        )  # Lock for thread-safe operations on error_urls

    def _web_crawler_thread(self, thread_id: int, urls: list):
        # Thread function to crawl each URL
        try:
            print(f"Starting web crawler thread {thread_id}")
            start_time = time.time()

            url = urls[thread_id]
            scraper = WebScraper()
            content = scraper.scrape_url(url, 0)

            # If the scraped content is too short, try extending the crawl rules
            if 0 < len(content) < 800:
                content = scraper.scrape_url(url, 1)

            # If the content length is sufficient, add it to the shared list
            if len(content) > 300:
                with self.web_contents_lock:
                    self.web_contents.append({"url": url, "content": content})

            end_time = time.time()
            print(
                f"Thread {thread_id} completed! Time consumed: {end_time - start_time:.2f}s"
            )

        except Exception as e:
            # Handle any exceptions, log the error, and store the URL
            with self.error_urls_lock:
                self.error_urls.append(url)
            print(f"Thread {thread_id}: Error crawling {url}: {e}")

    def _serper_launcher(self):
        # Function to launch the Serper client and get search results
        serper_client = SerperClient(config_path=self.config_path)
        serper_args = self.search_args.get(WebContentFetcher.SearchServices.SERPER, {})
        serper_results = serper_client.serper(self.query, **serper_args)
        return serper_client.extract_components(serper_results)

    def _bing_web_search_launcher(self):
        # Function to launch the Bing Web Search client and get search results
        bing_web_search_client = BingWebSearchClient(config_path=self.config_path)
        bing_web_search_args = self.search_args.get(
            WebContentFetcher.SearchServices.BING_WEB_SEARCH, {}
        )
        bing_web_search_results = bing_web_search_client.bing_web_search(
            self.query, **bing_web_search_args
        )
        return bing_web_search_client.extract_components(bing_web_search_results)

    def _bing_news_search_launcher(self):
        # Function to launch the Bing News Search client and get search results
        bing_news_search_client = BingNewsSearchClient(config_path=self.config_path)
        bing_news_search_args = self.search_args.get(
            WebContentFetcher.SearchServices.BING_NEWS_SEARCH, {}
        )
        bing_news_search_results = bing_news_search_client.bing_news_search(
            self.query, **bing_news_search_args
        )
        return bing_news_search_client.extract_components(bing_news_search_results)

    def _crawl_threads_launcher(self, url_list):
        # Create and start threads for each URL in the list
        threads = []
        for i in range(len(url_list)):
            thread = threading.Thread(
                target=self._web_crawler_thread, args=(i, url_list)
            )
            threads.append(thread)
            thread.start()
        # Wait for all threads to finish execution
        for thread in threads:
            thread.join()

    def fetch(self):
        # Main method to fetch web content based on the query and search service
        service_responses = []

        if self.SearchServices.SERPER in self.search_services:
            service_responses.append(self._serper_launcher())
        if self.SearchServices.BING_WEB_SEARCH in self.search_services:
            service_responses.append(self._bing_web_search_launcher())
        if self.SearchServices.BING_NEWS_SEARCH in self.search_services:
            service_responses.append(self._bing_news_search_launcher())

        if any(service_responses) and len(service_responses) == 1:
            service_response = service_responses[0]
            url_list = service_response["links"]
            self._crawl_threads_launcher(url_list)
            # Reorder the fetched content to match the order of URLs
            ordered_contents = [
                next(
                    (
                        item["content"]
                        for item in self.web_contents
                        if item["url"] == url
                    ),
                    "",
                )
                for url in url_list
            ]
            return ordered_contents, service_response

        elif any(service_responses) and len(service_responses) > 1:
            url_list = [
                link for response in service_responses for link in response["links"]
            ]
            self._crawl_threads_launcher(url_list)
            # Reorder the fetched content to match the order of URLs
            ordered_contents = [
                next(
                    (
                        item["content"]
                        for item in self.web_contents
                        if item["url"] == url
                    ),
                    "",
                )
                for url in url_list
            ]

            # combine responses from each search service
            combined_responses = {}

            search_queries = set(response["query"] for response in service_responses)
            if len(search_queries) > 1:
                raise ValueError(
                    "Different queries were used across multiple search services."
                )
            else:
                combined_responses["query"] = search_queries.pop()

            search_query_languages = set(
                response["language"] for response in service_responses
            )
            if len(search_query_languages) > 1:
                raise ValueError(
                    "Different queries were used across multiple search services."
                )
            else:
                combined_responses["language"] = search_query_languages.pop()

            combined_responses["count"] = sum(
                response["count"] for response in service_responses
            )
            combined_responses["titles"] = [
                title for response in service_responses for title in response["titles"]
            ]
            combined_responses["links"] = [
                link for response in service_responses for link in response["links"]
            ]
            combined_responses["snippets"] = [
                snippet
                for response in service_responses
                for snippet in response["snippets"]
            ]

            return ordered_contents, combined_responses

        return [], None
