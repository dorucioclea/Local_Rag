from local_rag import LocalRag
import streamlit as st
import os


# Temp storage of document file
def save_uploaded_file(directory, file):
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = os.path.join(directory, file.name)
    with open(full_path, "wb") as f:
        f.write(file.getbuffer())


config_file = "config_real.yaml"
rag_class = LocalRag(config_file)

# Page setup
st.set_page_config(
    page_title="Document Manager"
    )
st.title("Document Manager")
st.subheader("Document Upload")

# Form setup
name_in_db = st.text_input("Document name")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
upload_file = st.button("Upload File")

# Get the documents on file
document_list = rag_class.get_sql_documents()

# Chunking option for uploading document
chunking_options = {
    'Simple': 'simple',
    'Small to big': 'small_to_big'
}
chunk_option = st.radio("Select a chunking strategy:", options=chunking_options)
chunk_strategy = chunking_options[chunk_option]


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
st.subheader("Add To Document")

# Making sure there are documents to add to
if document_list != []:
    # Mapping for selecting a document name and id to add the text to with a dropdown
    add_pdf_mapping = {entry[1]: [entry[2], entry[3]] for entry in document_list}

    # Form setup
    add_document_name = st.selectbox("Add to document", options=list(add_pdf_mapping.keys()))
    add_pdf_id = add_pdf_mapping[add_document_name][0]
    add_chunk_strategy = add_pdf_mapping[add_document_name][1]
    add_uploaded_file = st.file_uploader("Choose a file to add", type=["pdf", "txt", "docx"])
    add_upload_file = st.button("Add File")

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
                    list_to_embed, paragraph_keys, _ = rag_class.pdf_document_reader(add_uploaded_file.name, name_in_db, chunk_strategy=add_chunk_strategy, add_to_doc=True)

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

st.subheader("Delete Document")
if document_list != []:
    # Create a dropdown menu for documents to display with id
    del_pdf_mapping = {entry[1]: entry[2] for entry in document_list}

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