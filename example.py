import json
import os
import time

import yaml
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings

from online_research_engine.fetch_web_content import WebContentFetcher
from online_research_engine.llm_answer import GPTAnswer
from online_research_engine.locate_reference import ReferenceLocator
from online_research_engine.retrieval import EmbeddingRetriever

if __name__ == "__main__":

    # Load configuration from a YAML file
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
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
    web_contents_fetcher = WebContentFetcher(query, config_path=config_path)
    web_contents, services_response = web_contents_fetcher.fetch()

    # Retrieve relevant documents using embeddings
    retriever = EmbeddingRetriever(embedding_model=embedding_model)
    relevant_docs_list = retriever.retrieve_embeddings(
        web_contents, services_response["links"], query
    )
    content_processor = GPTAnswer(llm=llm, config_path=config_path)
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

    # Optional Part: display the reference sources of the quoted sentences in LLM's answer
    print("\n\n", "=" * 30, "Reference Cards: ", "=" * 30, "\n")
    locator = ReferenceLocator(answer, services_response)
    reference_cards = locator.locate_source()
    json_formatted_cards = json.dumps(reference_cards, indent=4)
    print(json_formatted_cards)
