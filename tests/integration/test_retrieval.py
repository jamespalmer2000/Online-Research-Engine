import unittest

from online_research_engine.fetch_web_content import WebContentFetcher
from online_research_engine.retrieval import EmbeddingRetriever


class TestEmbeddingRetriever(unittest.TestCase):
    def test_embedding_retriever(self):
        import os

        import yaml
        from langchain.embeddings import AzureOpenAIEmbeddings

        # Load configuration from a YAML file
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        embedding_model = AzureOpenAIEmbeddings(
            model=config["azure_embed_deployment"],
            azure_endpoint=config["azure_endpoint"],
            openai_api_key=config["azure_openai_api_key"],
            openai_api_version=config["azure_openai_api_version"],
        )

        query = "What happened to Silicon Valley Bank"

        # Create a WebContentFetcher instance and fetch web contents
        web_contents_fetcher = WebContentFetcher(query)
        web_contents, services_response = web_contents_fetcher.fetch()

        # Create an EmbeddingRetriever instance and retrieve relevant documents
        retriever = EmbeddingRetriever(embedding_model=embedding_model)
        relevant_docs_list = retriever.retrieve_embeddings(
            web_contents, services_response["links"], query
        )

        print("\n\nRelevant Documents from VectorDB:\n", relevant_docs_list)


if __name__ == "__main__":
    unittest.main()
