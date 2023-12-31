from local_rag import LocalRag
import streamlit as st
import os
import yaml


st.set_page_config(page_title="Content Generator")
st.title("Content Generator")
st.subheader("Write short form content about your documents.")
st.write("Your document stores are an aggregate of all the documents and YouTube videos you upload into them.")

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


if check_yaml_population(config_file, required_keys):
    rag_class = LocalRag(config_file)

    # Get the documents on file
    document_list = rag_class.get_sql_documents()

    if document_list != []:
        content_query = st.text_input("What do you want to know")

        pdf_mapping = {entry[2]: entry[3] for entry in document_list}

        # Create a dropdown menu
        selected_pdf_name = st.selectbox("Select a document", options=list(pdf_mapping.keys()))

        # Display the selected PDF ID
        selected_pdf_id = pdf_mapping[selected_pdf_name]

        k = st.slider("Sources to retrieve.", 1 , 10, 5)

        # Chunking option for uploading document
        reranking_option = {
            'No reranking': 'no',
            'Reranking': 'rerank'
        }
        rank_option = st.radio("Select reranking:", options=reranking_option)
        rank_strategy = reranking_option[rank_option]

        query = st.button("Generate Content")

        if query:
            with st.status("Answering query...", expanded=True) as status:
                # Reranking strategy and setting K depending on it
                st.write("Searching for results...")
                if rank_strategy == "rerank":
                    paragraph_id_list, cosine_results = rag_class.retrieve_documents(content_query, k*4, selected_pdf_id)
                else:
                    paragraph_id_list, cosine_results = rag_class.retrieve_documents(content_query, k, selected_pdf_id)

                # Getting sources
                st.write("Searching for sources...")
                sources_list = rag_class.get_paragraph_sources(paragraph_id_list)

                # Reranking strategy
                if rank_strategy == "rerank":
                    st.write("Re-ranking sources...")
                    sorted_sources = rag_class.rerank_sources(content_query, sources_list)
                    sorted_sources = sorted_sources[:k]
                    context_for_llm = "".join(sorted_sources)
                else:
                    sorted_sources = sources_list
                    context_for_llm = "".join(sources_list)

                # Send to LLM
                st.write("Sending to AI...")
                answer = rag_class.make_llm_request(content_query, context_for_llm, gen_content=True)
                status.update(label="Answer found!", state="complete", expanded=False)

            st.markdown(answer)

            for idx, item in enumerate(sorted_sources):
                with st.expander(f"Source {idx + 1}"):
                    st.markdown(item)

    else:
        st.markdown("Please upload some documents.")

else:
    st.write("Your settings are not filled out correctly.")
