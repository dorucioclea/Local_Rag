from local_rag import LocalRag
import streamlit as st

st.title("Document Search")

config_file = "config_real.yaml"
rag_class = LocalRag(config_file)

# Get the documents on file
document_list = rag_class.get_sql_documents() 

if document_list != []:
	query = st.chat_input("What do you want to know")
	
	pdf_mapping = {entry[1]: entry[2] for entry in document_list}

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

	if query:
		st.write(f"User: {query}")

		with st.status("Answering query...", expanded=True) as status:
			# Reranking strategy and setting K depending on it
			st.write("Searching for results...")
			if rank_strategy == "rerank":
				paragraph_id_list, cosine_results = rag_class.retrieve_documents(query, k*4, selected_pdf_id)
			else:
				paragraph_id_list, cosine_results = rag_class.retrieve_documents(query, k, selected_pdf_id)

			# Getting sources
			st.write("Searching for sources...")
			sources_list = rag_class.get_paragraph_sources(paragraph_id_list)

			# Reranking strategy
			if rank_strategy == "rerank":
				st.write("Re-ranking sources...")
				sorted_sources = rag_class.rerank_sources(query, sources_list)
				sorted_sources = sorted_sources[:k]
				context_for_llm = "".join(sorted_sources)
			else:
				sorted_sources = sources_list
				context_for_llm = "".join(sources_list)

			# Send to LLM
			st.write("Sending to AI...")
			answer = rag_class.make_llm_request(query, context_for_llm)
			status.update(label="Answer found!", state="complete", expanded=False)

		with st.chat_message("assistant"):
			st.write(answer)

		for idx, item in enumerate(sorted_sources):
			with st.expander(f"Source {idx + 1}"):
				st.markdown(item)

else:
	st.markdown("Please upload some documents.")