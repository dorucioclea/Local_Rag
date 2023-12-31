import os
import yaml
from .document_reader import DocumentReader
from .database import VectorDatabase, DocumentDB, DocumentTextDB
from .ml_models import OllamaLLM, EmbeddingClass, EmbeddingReranker


class LocalRag:
    def __init__(self, config_file):
        self.config_file = config_file
        with open(self.config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self.temp_storage = data_loaded["temp_doc_storage"]
        self.document_reader_instance = DocumentReader()

    def document_reader(self, load_func_str, file_name, doc_name, chunk_strategy, add_to_doc=False):
        if not doc_name:
            raise ValueError("doc_name cannot be empty.")

        if chunk_strategy is None:
            raise ValueError("Invalid chunk_strategy. It cannot be None.")

        load_func = getattr(self.document_reader_instance, load_func_str, None)

        if not callable(load_func):
            raise TypeError(f"{load_func_str} should be a method of DocumentReader")

        try:
            document_db = DocumentDB(self.config_file)
            paragraph_list, paragraph_keys, doc_id, big_string_list = load_func(f"{self.temp_storage}/{file_name}",
                                                                                chunk_strategy)
        except Exception as e:
            raise ValueError("Error in load_func execution.") from e

        if not add_to_doc:
            try:
                document_db.add_document(doc_name, doc_id, chunk_strategy)
            except Exception as e:
                raise ValueError("Error in add_document execution.") from e

        try:
            doc_text_db = DocumentTextDB(self.config_file)
            data_in = []

            for paragraph_id, paragraph in zip(paragraph_keys, big_string_list):
                data_in.append((doc_name, doc_id, paragraph_id, paragraph))
            doc_text_db.add_bulk_documents(data_in)
        except Exception as e:
            raise ValueError("Error in adding document texts.") from e

        return paragraph_list, paragraph_keys, doc_id

    def youtube_reader_helper(self, file_name, doc_name, chunk_strategy, add_to_doc=False):
        document_db = DocumentDB(self.config_file)
        paragraph_list, paragraph_keys, doc_id, big_string_list = self.document_reader_instance.load_youtube(file_name, chunk_strategy)

        if not add_to_doc:
            try:
                document_db.add_document(doc_name, doc_id, chunk_strategy)
            except Exception as e:
                raise ValueError("Error in add_document execution.") from e

        try:
            doc_text_db = DocumentTextDB(self.config_file)
            data_in = []

            for paragraph_id, paragraph in zip(paragraph_keys, big_string_list):
                data_in.append((doc_name, doc_id, paragraph_id, paragraph))
            doc_text_db.add_bulk_documents(data_in)
        except Exception as e:
            raise ValueError("Error in adding document texts.") from e

        return paragraph_list, paragraph_keys, doc_id

    def pdf_document_reader(self, file_name, doc_name, chunk_strategy, add_to_doc=False):
        try:
            return self.document_reader("load_pdf", file_name, doc_name, chunk_strategy, add_to_doc)
        except Exception as e:
            raise ValueError("Error while reading pdf document.") from e

    def txt_document_reader(self, file_name, doc_name, chunk_strategy, add_to_doc=False):
        try:
            return self.document_reader("load_txt", file_name, doc_name, chunk_strategy, add_to_doc)
        except Exception as e:
            raise ValueError("Error while reading txt document.") from e

    def docx_document_reader(self, file_name, doc_name, chunk_strategy, add_to_doc=False):
        try:
            return self.document_reader("load_docx", file_name, doc_name, chunk_strategy, add_to_doc)
        except Exception as e:
            raise ValueError("Error while reading docx document.") from e

    def youtube_reader(self, file_name, doc_name, chunk_strategy, add_to_doc=False):
        try:
            return self.youtube_reader_helper(file_name, doc_name, chunk_strategy, add_to_doc)
        except Exception as e:
            raise ValueError("Error while reading pdf document.") from e

    def create_batch_embeddings(self, pdf_in, doc_id):
        if pdf_in is None or not isinstance(pdf_in, list):
            raise ValueError("Invalid pdf_in. It should be a list of paragraphs.")

        if doc_id is None:
            raise ValueError("Invalid doc_id. It cannot be None.")

        try:
            embedding_class = EmbeddingClass(self.config_file)

            # Create vector batch
            emb_list = [{"text": item["paragraph"]} for item in pdf_in]
            embedding = embedding_class.batch_embedding(emb_list)

        except Exception as e:
            raise ValueError("Error in creating batch embeddings.") from e

        return embedding

    def load_documents_db(self, embeddings: list, paragraph_keys: list, doc_id: str) -> None:
        if not embeddings or not isinstance(embeddings, list):
            raise ValueError("Invalid embeddings. They should be provided as a list.")

        if not paragraph_keys or not isinstance(paragraph_keys, list):
            raise ValueError("Invalid paragraph_keys. They should be provided as a list.")

        if doc_id is None or not isinstance(doc_id, str) or doc_id == "":
            raise ValueError("Invalid doc_id. It cannot be None or an empty string.")

        vec_db = VectorDatabase(self.config_file, doc_id)
        vec_db.insert_batch_vecs(embeddings, doc_id, paragraph_keys)
        vec_db.make_cosine_index()

    def retrieve_documents(self, prompt: str, k: int, doc_id: str) -> tuple[list, list]:
        if prompt is None or not isinstance(prompt, str) or prompt == "":
            raise ValueError("Invalid prompt. Make sure it's a valid string.")

        if k is None or not isinstance(k, int) or k <= 0:
            raise ValueError("Invalid value for k. It should be an integer greater than 0.")

        if doc_id is None or not isinstance(doc_id, str) or doc_id == "":
            raise ValueError("Invalid doc_id. It cannot be None or an empty string.")

        embedding_class = EmbeddingClass(self.config_file)
        vec_db = VectorDatabase(self.config_file, doc_id)

        query_emb = embedding_class.return_embedding(prompt)
        results = vec_db.get_matches(query_emb, k)

        cosine_sim = [d[1] for d in results]
        paragraph_id_list = [d[2]["paragraph_id"] for d in results]

        return paragraph_id_list, cosine_sim

    def get_paragraph_sources(self, paragraph_id_list: list) -> list:
        if not paragraph_id_list or not isinstance(paragraph_id_list, list):
            raise ValueError("Invalid paragraph_id_list. It should be a list.")

        source_list = []

        for paragraph_id in paragraph_id_list:
            doc_text_db = DocumentTextDB(self.config_file)
            source_list.append(doc_text_db.get_big_from_small(paragraph_id))

        return source_list

    @staticmethod
    def rerank_sources(query: str, sources: list) -> list:
        if query is None or not isinstance(query, str) or query == "":
            raise ValueError("Invalid query. Make sure it's a valid string.")

        if sources is None or not isinstance(sources, list):
            raise ValueError("Invalid sources. They should be a list of sources.")

        reranker = EmbeddingReranker()
        ranked_sources = reranker.rerank_data(query, sources)

        return ranked_sources

    def make_llm_request(self, prompt: str, context: str, gen_content: bool = False) -> str:
        if prompt is None or not isinstance(prompt, str) or prompt == "":
            raise ValueError("Invalid prompt. Make sure it's a valid string.")

        if context is None or not isinstance(context, str) or context == "":
            raise ValueError("Invalid context. Make sure it's a valid string.")

        ollama_llm = OllamaLLM(self.config_file)
        result = ollama_llm.chat_request(prompt, context, gen_content)

        return result

    def get_sql_documents(self) -> list:
        document_db = DocumentDB(self.config_file)
        return document_db.get_docs()

    def delete_docs(self, doc_id: str) -> None:
        if doc_id is None or not isinstance(doc_id, str) or doc_id == "":
            raise ValueError("Invalid doc_id. It cannot be None or an empty string.")

        document_db = DocumentDB(self.config_file)
        vec_db = VectorDatabase(self.config_file, doc_id)
        doc_text_db = DocumentTextDB(self.config_file)

        vec_db.delete_vecs()
        document_db.delete_document(doc_id)
        doc_text_db.delete_document(doc_id)
