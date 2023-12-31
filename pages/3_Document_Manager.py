from local_rag import LocalRag
import streamlit as st
import yaml
import os


# Temp storage of document file
def save_uploaded_file(directory, file):
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = os.path.join(directory, file.name)
    with open(full_path, "wb") as f:
        f.write(file.getbuffer())


if os.path.isfile("config_real.yaml"):
    config_file = "config_real.yaml"
else:
    config_file = "config.yaml"

required_keys = ["database_name", "user", "password", "host", "db_port", "embedding_batches",
                 "model_name", "ollama_api_url", "temperature"]


def check_yaml_population(yaml_file, required_keys):
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)

        if not data:
            return False

        for key in required_keys:
            if key not in data or data[key] is None:
                return False

            elif data[key] == '':
                return False

        return True
    except Exception as e:
        print(f"Error checking YAML file: {e}")
        return False


# Page setup
st.set_page_config(page_title="Document Manager")
st.title("Document Manager")
st.subheader("Upload Document")
st.write("Create a searchable document store by adding your own txt, pdf or docx documents. You can multiple documents to this searchable storage")

if check_yaml_population(config_file, required_keys):
    rag_class = LocalRag(config_file)
    # Form setup
    name_in_db = st.text_input("Document name")
    uploaded_file = st.file_uploader("Choose a file to add", key="new_vid", type=["pdf", "txt", "docx"])

    # Get the documents on file
    document_list = rag_class.get_sql_documents()

    # Chunking option for uploading document
    chunking_options = {
        'Simple': 'simple',
        'Small to big': 'small_to_big'
    }
    chunk_option = st.radio("Document chunking strategy:", options=chunking_options)
    chunk_strategy = chunking_options[chunk_option]
    upload_file = st.button("Embed Document")


    # Upload a new document
    if upload_file and name_in_db != "":
        if uploaded_file is not None:
            # Save the file to a folder
            current_working_directory = os.getcwd()
            file_directory = os.path.join(current_working_directory, "temp_doc_storage")

            with st.status("Uploading document...", expanded=True) as status:
                st.write("Uploading file...")
                save_uploaded_file(file_directory, uploaded_file)

                st.write("Breaking up document...")
                if uploaded_file.type == "application/pdf":
                    list_to_embed, paragraph_keys, doc_id = rag_class.pdf_document_reader(uploaded_file.name, name_in_db, chunk_strategy=chunk_strategy)

                elif uploaded_file.type == "text/plain":
                    list_to_embed, paragraph_keys, doc_id = rag_class.txt_document_reader(uploaded_file.name, name_in_db, chunk_strategy=chunk_strategy)

                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    list_to_embed, paragraph_keys, doc_id = rag_class.docx_document_reader(uploaded_file.name, name_in_db, chunk_strategy=chunk_strategy)

                st.write("Generating vectors...")
                embeddings = rag_class.create_batch_embeddings(list_to_embed, doc_id)

                st.write("Adding vectors into vector database...")
                rag_class.load_documents_db(embeddings, paragraph_keys, doc_id)

                st.write("Cleaning up...")
                os.remove(os.path.join(file_directory, uploaded_file.name))

                status.update(label="Upload completed!", state="complete", expanded=False)


    st.divider()
    st.subheader("Upload YouTube Video")
    st.write("Create a searchable storage for the transcript of a YouTube video. You can multiple documents to this searchable storage.")
    video_in_db = st.text_input("Document name", key="id_in")
    youtube_link = st.text_input("YouTube ID")
    chunk_option = st.radio("Video chunking strategy:", options=chunking_options)
    chunk_strategy = chunking_options[chunk_option]
    embed_video = st.button("Embed YouTube Video")

    if embed_video and video_in_db != "":
        if youtube_link is not None:
            with st.status("Uploading document...", expanded=True) as status:
                st.write("Uploading transcript...")
                list_to_embed, paragraph_keys, doc_id = rag_class.youtube_reader(youtube_link, video_in_db, chunk_strategy=chunk_strategy)

                st.write("Generating vectors...")
                embeddings = rag_class.create_batch_embeddings(list_to_embed, doc_id)

                st.write("Adding vectors into vector database...")
                rag_class.load_documents_db(embeddings, paragraph_keys, doc_id)

                status.update(label="Upload completed!", state="complete", expanded=False)


    st.divider()
    st.subheader("Add Additional Document")
    st.write("Add additional txt, pdf or docx documents to your document store. You can add this to any document store you have, including to YouTube videos.")

    # Making sure there are documents to add to
    if document_list != []:
        # Mapping for selecting a document name and id to add the text to with a dropdown
        add_pdf_mapping = {entry[2]: [entry[3], entry[4]] for entry in document_list}

        # Form setup
        add_document_name = st.selectbox("Add to document", options=list(add_pdf_mapping.keys()))
        add_pdf_id = add_pdf_mapping[add_document_name][0]
        add_chunk_strategy = add_pdf_mapping[add_document_name][1]
        add_uploaded_file = st.file_uploader("Choose a file to add", type=["pdf", "txt", "docx"])
        add_upload_file = st.button("Add Document")

        # Algorithm to add a document
        if add_upload_file:
            if add_uploaded_file is not None:
                # Save the file to a folder
                current_working_directory = os.getcwd()
                file_directory = os.path.join(current_working_directory, "temp_doc_storage")

                with st.status("Adding document...", expanded=True) as status:
                    st.write("Uploading file...")
                    save_uploaded_file(file_directory, add_uploaded_file)

                    st.write("Breaking up document...")
                    if add_uploaded_file.type == "application/pdf":
                        list_to_embed, paragraph_keys, _ = rag_class.pdf_document_reader(add_uploaded_file.name, add_document_name, chunk_strategy=add_chunk_strategy, add_to_doc=True)

                    elif add_uploaded_file.type == "text/plain":
                        list_to_embed, paragraph_keys, _ = rag_class.txt_document_reader(add_uploaded_file.name, name_in_db, chunk_strategy=add_chunk_strategy, add_to_doc=True)

                    elif add_uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        list_to_embed, paragraph_keys, _ = rag_class.docx_document_reader(add_uploaded_file.name, name_in_db, chunk_strategy=add_chunk_strategy, add_to_doc=True)

                    st.write("Generating vectors...")
                    embeddings = rag_class.create_batch_embeddings(list_to_embed, add_pdf_id)

                    st.write("Adding vectors into vector database...")
                    rag_class.load_documents_db(embeddings, paragraph_keys, add_pdf_id)

                    st.write("Cleaning up...")
                    os.remove(os.path.join(file_directory, add_uploaded_file.name))

                    status.update(label="Upload completed!", state="complete", expanded=False)

    else:
        st.markdown("First add documents.")


    st.divider()
    st.subheader("Add Additional YouTube Video")
    st.write("Add additional YouTube Video to your document store. You can add this to any document store you have, including to document stores.")

    # Making sure there are documents to add to
    if document_list != []:
        # Mapping for selecting a document name and id to add the text to with a dropdown
        add_pdf_mapping = {entry[2]: [entry[3], entry[4]] for entry in document_list}

        # Form setup
        add_youtube_name = st.selectbox("Add to document", key="yt_name", options=list(add_pdf_mapping.keys()))
        add_video_id = add_pdf_mapping[add_youtube_name][0]
        add_chunk_strategy = add_pdf_mapping[add_youtube_name][1]
        add_youtube_link = st.text_input("YouTube ID", key="add_link")
        add_youtube_file = st.button("Add YouTube Video")

        # Algorithm to add a document
        if add_youtube_file:
            if add_youtube_link is not None:
                with st.status("Uploading document...", expanded=True) as status:
                    st.write("Uploading transcript...")
                    list_to_embed, paragraph_keys, _ = rag_class.youtube_reader(add_youtube_link, add_youtube_name, chunk_strategy=add_chunk_strategy, add_to_doc=True)

                    st.write("Generating vectors...")
                    embeddings = rag_class.create_batch_embeddings(list_to_embed, add_video_id)

                    st.write("Adding vectors into vector database...")
                    rag_class.load_documents_db(embeddings, paragraph_keys, add_video_id)

                    status.update(label="Upload completed!", state="complete", expanded=False)

    else:
        st.markdown("First add documents.")

    st.divider()

    st.subheader("Delete Document")
    st.write("Delete a document store, this cannot be undone.")
    if document_list != []:
        # Create a dropdown menu for documents to display with id
        del_pdf_mapping = {entry[2]: entry[3] for entry in document_list}

        # Making the form
        del_pdf_name = st.selectbox("Select a document", options=list(del_pdf_mapping.keys()))
        del_pdf_id = del_pdf_mapping[del_pdf_name]
        delete_docs = st.button("Delete")

        # Deleting documents
        if delete_docs:
            with st.status("Deleting document...", expanded=True) as status:
                st.write("Deleting document...")
                rag_class.delete_docs(del_pdf_id)
                status.update(label="Document deleted!", state="complete", expanded=False)

    else:
        st.markdown("No documents uploaded.")

else:
    st.write("Your settings are not filled out correctly.")
