from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


class EmbeddingRetriever:
    TOP_K = 10  # Number of top K documents to retrieve

    def __init__(self, embedding_model):
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=0
        )

        self.embedding_model = embedding_model

    def retrieve_embeddings(self, contents_list: list, link_list: list, query: str):
        # Retrieve embeddings for a given list of contents and a query
        metadatas = [{"url": link} for link in link_list]
        texts = self.text_splitter.create_documents(contents_list, metadatas=metadatas)

        # Create a Chroma database from the documents using specific embeddings
        db = Chroma.from_documents(
            texts,
            self.embedding_model,
        )

        # Create a retriever from the database to find relevant documents
        retriever = db.as_retriever(search_kwargs={"k": self.TOP_K})
        relevant_documents = retriever.get_relevant_documents(
            query
        )  # Retrieve and return the relevant documents

        # Explicitly delete the collection
        db.delete_collection()
        del db

        return relevant_documents
