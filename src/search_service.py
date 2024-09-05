class SearchClientInterface():
    def __init__(self):
        """Initialize the Search Client"""
        pass

    def service(self, query: str) -> dict:
        """Create and perform a request to the service and return the JSON response."""
        pass

    def _contains_chinese(self, query: str) -> bool:
        """Check if a string contains Chinese characters using a regular expression."""
        pass

    def extract_components(self, service_response: dict) -> dict:
        """Extract and return organic search results from the service"""
        pass
