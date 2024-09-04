import yaml
import os
from fetch_web_content import WebContentFetcher
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings

class EmbeddingRetriever:
    TOP_K = 10  # Number of top K documents to retrieve

    def __init__(self, embedding_model):
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0
        )

        self.embedding_model = embedding_model

    def retrieve_embeddings(self, contents_list: list, link_list: list, query: str):
        # Retrieve embeddings for a given list of contents and a query
        metadatas = [{'url': link} for link in link_list]
        texts = self.text_splitter.create_documents(contents_list, metadatas=metadatas)

        # Create a Chroma database from the documents using specific embeddings
        db = Chroma.from_documents(
            texts,
            self.embedding_model,
        )

        # Create a retriever from the database to find relevant documents
        retriever = db.as_retriever(search_kwargs={"k": self.TOP_K})
        relevant_documents = retriever.get_relevant_documents(query) # Retrieve and return the relevant documents

        # Explicitly delete the collection 
        db.delete_collection() 
        del db

        return relevant_documents

# Example usage
if __name__ == "__main__":
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
    web_contents, serper_response = web_contents_fetcher.fetch()

    # Create an EmbeddingRetriever instance and retrieve relevant documents
    retriever = EmbeddingRetriever(embedding_model=embedding_model)
    relevant_docs_list = retriever.retrieve_embeddings(web_contents, serper_response['links'], query)

    print("\n\nRelevant Documents from VectorDB:\n", relevant_docs_list)
    