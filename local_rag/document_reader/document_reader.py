import PyPDF2
import secrets
import string
import nltk
from nltk.tokenize import sent_tokenize
from youtube_transcript_api import YouTubeTranscriptApi
from docx import Document


class DocumentReader:
    """
    DocumentReader

    Class for reading and processing documents.

    Attributes:
        None

    Methods:
        _doc_key_gen() -> str:
            Generates a random key ID for a document.

        _paragraph_key_gen() -> str:
            Generates a random key ID for a paragraph.

        _split_text_into_chunks(self, text, chunk_size, overlap) -> tuple[list[str], list[str]]:
            Splits the text into chunks with a specified size and overlap.

        _split_text_into_sentences(self, text, sentences_chunk=8) -> tuple[list[float], list[str], list[str]]:
            Splits the text into sentences and constructs them into paragraphs.

        _text_splitter(self, page, chunk_strategy, chunk_size=300, overlap=50) -> tuple[list[str], list[str], list[str]]:
            Splits the text based on the given chunk_strategy.

        _make_paragraph_list(page_chunks, doc_id) -> list[dict[str, str]]:
            Creates a list of paragraphs with a document ID.

        load_pdf(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
            Loads a PDF file, splits it into paragraphs, and returns the paragraphs, paragraph keys, document ID, and
            big string list.

        load_txt(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
            Loads a TXT file, splits it into paragraphs, and returns the paragraphs, paragraph keys, document ID, and
            big string list.

        load_docx(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
            Loads a DOCX file, splits it into paragraphs, and returns the paragraphs, paragraph keys, document ID, and
            big string list.
    """
    @staticmethod
    def _doc_key_gen() -> str:
        characters = string.ascii_letters + string.digits
        key_id = ''.join(secrets.choice(characters) for _ in range(15))

        return key_id

    @staticmethod
    def _paragraph_key_gen() -> str:
        characters = string.ascii_letters + string.digits
        key_id = ''.join(secrets.choice(characters) for _ in range(20))

        return key_id

    @staticmethod
    def _get_transcript_api(video_id) -> str:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ""

        for idx, line in enumerate(transcript):
            if idx % 3 == 0 and idx != 0:
                transcript_text = transcript_text + ". " + line["text"]

            else:
                transcript_text = transcript_text + "" + line["text"]

        return transcript_text

    def _split_text_into_chunks(self, text, chunk_size, overlap) -> tuple[list[str], list[str]]:
        words = text.split()
        num_words = len(words)
        paragraph_keys = []

        # Calculate the number of chunks needed
        total_chunk_length = chunk_size - overlap
        num_chunks = (num_words + total_chunk_length - 1) // total_chunk_length

        # Adjust chunk size to make the chunks as even as possible
        even_chunk_size = (num_words + num_chunks - 1) // num_chunks
        chunks = []

        # Make the chunks and give each chunk a key
        for i in range(0, num_words, even_chunk_size):
            chunk_end = min(i + even_chunk_size + overlap, num_words)
            chunk = ' '.join(words[i:chunk_end])
            chunks.append(chunk)
            paragraph_keys.append(self._paragraph_key_gen())

        return chunks, paragraph_keys

    def _split_text_into_sentences(self, text, sentences_chunk=8) -> tuple[list[float], list[str], list[str]]:

        # Load model to split a block of text into a list of sentences
        nltk.download('punkt')
        sentences = sent_tokenize(text)

        embedding_text_list = []
        big_string_list = []
        paragraph_keys = []

        # Loop through the sentences and construct them into paragraphs
        for x in range(len(sentences)):
            if x - sentences_chunk // 2 < 0:
                embedding_text_list.append(sentences[x])
                big_string_list.append(" ".join(sentences[0: sentences_chunk]))

            elif x - sentences_chunk // 2 >= 0 and x + sentences_chunk // 2 <= len(sentences):
                embedding_text_list.append(sentences[x])
                big_string_list.append(" ".join(sentences[x - sentences_chunk // 2: x + sentences_chunk // 2]))

            elif x + sentences_chunk // 2 > len(sentences):
                embedding_text_list.append(sentences[x])
                big_string_list.append(" ".join(sentences[len(sentences) - sentences_chunk:]))

            else:
                print("Logic error")

            # Give each paragraph a key
            paragraph_keys.append(self._paragraph_key_gen())

        return embedding_text_list, paragraph_keys, big_string_list

    def _text_splitter(self, page, chunk_strategy, chunk_size=300, overlap=50) -> tuple[list[str], list[str], list[str]]:
        if chunk_strategy == "simple":
            page_chunks, paragraph_keys = self._split_text_into_chunks(page, chunk_size, overlap)
            big_string_list = page_chunks

        if chunk_strategy == "smalltobig":
            page_chunks, paragraph_keys, big_string_list = self._split_text_into_sentences(page)

        return page_chunks, paragraph_keys, big_string_list

    @staticmethod
    def _make_paragraph_list(page_chunks, doc_id) -> list[dict[str, str]]:
        # Add each chunk into the database with a paragraph_key for each chunk
        paragraph_list = []

        for chunk in page_chunks:
            # Append the information for us
            paragraph_entry = {
                "doc_id": doc_id,
                "paragraph": chunk
            }
            paragraph_list.append(paragraph_entry)

        return paragraph_list

    def load_pdf(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
        doc_id = self._doc_key_gen()

        full_pdf_text = ""

        # Load the pdf with the filename
        with open(file_name, 'rb') as pdf_file:
            # Create a pdf reader object
            pdf_reader_object = PyPDF2.PdfReader(pdf_file)

            # Loop through each page
            for x in range(len(pdf_reader_object.pages)):
                # Creat a page object
                page_object = pdf_reader_object.pages[x]

                # Remove multiple spacing for the page and split into chunks of 200 words
                page = page_object.extract_text().replace("\n", " ")

                full_pdf_text = full_pdf_text + page

        page_chunks, paragraph_keys, big_string_list = self._text_splitter(full_pdf_text, chunk_strategy)
        paragraph_list = self._make_paragraph_list(page_chunks, doc_id)

        return paragraph_list, paragraph_keys, doc_id, big_string_list

    def load_txt(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
        doc_id = self._doc_key_gen()

        # Load the pdf with the filename
        with open(file_name, 'r') as file:
            txt_file = file.read()

        page_chunks, paragraph_keys, big_string_list = self._text_splitter(txt_file, chunk_strategy)
        paragraph_list = self._make_paragraph_list(page_chunks, doc_id)

        return paragraph_list, paragraph_keys, doc_id, big_string_list

    def load_docx(self, file_name, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
        doc_id = self._doc_key_gen()

        # Load the pdf with the filename
        doc = Document(file_name)
        list_docx = [paragraph.text for paragraph in doc.paragraphs]
        text_docx = "".join([item for item in list_docx])

        page_chunks, paragraph_keys, big_string_list = self._text_splitter(text_docx, chunk_strategy)
        paragraph_list = self._make_paragraph_list(page_chunks, doc_id)

        return paragraph_list, paragraph_keys, doc_id, big_string_list

    def load_youtube(self, youtube_id, chunk_strategy) -> tuple[list[dict[str, str]], list[str], str, list[str]]:
        doc_id = self._doc_key_gen()
        text_video = self._get_transcript_api(youtube_id)

        page_chunks, paragraph_keys, big_string_list = self._text_splitter(text_video, chunk_strategy)

        paragraph_list = self._make_paragraph_list(page_chunks, doc_id)

        return paragraph_list, paragraph_keys, doc_id, big_string_list
