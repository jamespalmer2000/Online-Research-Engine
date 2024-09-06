import os
import time
import unittest

import yaml
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings

from online_research_engine.fetch_web_content import WebContentFetcher
from online_research_engine.llm_answer import GPTAnswer
from online_research_engine.retrieval import EmbeddingRetriever


class TestGPTAnswer(unittest.TestCase):
    def test_gpt_answer(self):
        # Load configuration from a YAML file
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        llm = AzureChatOpenAI(
            model=config["azure_llm_deployment"],
            azure_endpoint=config["azure_endpoint"],
            openai_api_key=config["azure_openai_api_key"],
            openai_api_version=config["azure_openai_api_version"],
            callbacks=[StreamingStdOutCallbackHandler()],
        )

        embedding_model = AzureOpenAIEmbeddings(
            model=config["azure_embed_deployment"],
            azure_endpoint=config["azure_endpoint"],
            openai_api_key=config["azure_openai_api_key"],
            openai_api_version=config["azure_openai_api_version"],
        )

        query = "What happened to Silicon Valley Bank"
        output_format = ""  # User can specify output format
        profile = ""  # User can define the role for LLM

        # Fetch web content based on the query
        web_contents_fetcher = WebContentFetcher(query)
        web_contents, services_response = web_contents_fetcher.fetch()

        # Retrieve relevant documents using embeddings
        retriever = EmbeddingRetriever(embedding_model)
        relevant_docs_list = retriever.retrieve_embeddings(
            web_contents, services_response["links"], query
        )

        content_processor = GPTAnswer(llm)
        formatted_relevant_docs = content_processor._format_reference(
            relevant_docs_list, services_response["links"]
        )
        print(formatted_relevant_docs)

        # Measure the time taken to get an answer from the GPT model
        start = time.time()

        # Generate answer from ChatOpenAI
        ai_message_obj = content_processor.get_answer(
            query,
            formatted_relevant_docs,
            services_response["language"],
            output_format,
            profile,
        )
        answer = ai_message_obj.content + "\n"
        end = time.time()

        print(answer)

        print("\n\nGPT Answer time:", end - start, "s")


if __name__ == "__main__":
    unittest.main()
