## UPDATE 31/12/2023
1. I have included YouTube video embedding into the RAG application. This essentially uses the YouTube Subtitles API to get the subtitles, the subtitles are then embedded into the RAG application
2. Settings menue to edit the yaml file, this makes it easier to add in your postgress database information. From here you can select your own Ollama models as well.

---

# Local Rag

Local Rag uses local machine learning models for Retrieval Augmented Generation (RAG). The stack is Streamlit as the front end, Ollama and Transformers for the inference and Supabase for the database. This project offers an efficient, local, and private RAG system. The design is to keep document stores under names, in each store you can add in documents which can be searched. The idea is to aggregate specific information from different sources to search. You can upload PDF/txt/docx as well as YouTube video subtitles when you supply video id.

In addition, two advanced RAG features are included, small-to-big document chunking and retrieval re-ranking.

Local Rag offers two outputs based on your query, document question answering and the ability to generate a post/content based on your search query on the documents.

[<img src="https://github.com/puredatum/Local_Rag/blob/master/images/Untitled%20design.png" alt="Demonstration" title="Demonstration">](https://github.com/puredatum/Local_Rag/blob/master/images/Untitled%20design.png)

## Description

**Features**
- Upload and embed PDF/txt/docx as well as YouTube video subtitles
- Select your LLM model for any models on Ollama
- Simple document chunking. This chunks the sources and embeds the chunk, upon retrieval the entire embedded chunk is used for synthesis
- The Transformers package is used for embedding and retrieval re-ranking
- Query your named document group with a question
- Query your named document group with a topic to write a post on
- Shows sources for retrieval
- Fully local with Ollama and Transformers
- Embeddings are done in batches of n size, this can be chosen based on your GPU, the default is 64
- The database is free for anyone and is hosted by Supabase
- Handle multiple document groups
- Easily add more documents to a current document group
- At the moment the chat history isn't used or remembered

**Advanced Features**
- Small-to-big chunking: The source is broken in sentences which are embedded, the surrounding paragraph is then stored for retrieval when the corresponding embedding is retrieved
- Retrieval re-ranking of the sources using the 'BAAI/bge-reranker-large' model. K x 4 sources are retrieved and ranked, then the new top k sources are chosen

**Future Features**
- Enable chat with conversation history as additional context
- A docker container

## Setup & Installation
To get started with Local Rag, follow the steps below:

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using the following command:
    ```markdown
   pip install -r requirements.txt
   ```
4. Install [Ollama](https://github.com/jmorganca/ollama). Once installed, make sure to run it successfully. Make sure the Ollama model information is correct.
   ```markdown
   #Ollama LLM
   model_name: mistral
   ollama_api_url: http://localhost:11434/api/generate
   temperature: 0
   stream: False
   ```
5. Sign up for a free Supabase account
6. Set up your databases, you will need to make sure vecs are enable on Supabase. The app will create the tables for you, you just need to enable vecs and make the project and database.
7. Go into the settings menu to update the below settings to your own Supabase database:
```markdown
   database_name:
   user:
   password:
   host:
   db_port:
   ```

## Usage

The Local Rag project is designed with a user-friendly interface and easy maneuvering. Once you've successfully followed the setup and installation steps, you can start using it for your document management. 

Running steps:
1. Make sure Ollama is running and Supabase is set up properly, with the settings for your database set
2. Start the streamlit server by running the below in the terminal
```markdown
streamlit run 1_Document_Search.py
```
3. If you haven't loaded any documents, then you will not see anything on the search sections
4. Navigate to the Document Manager to upload pdf/txt/docx documents to a group that you name
5. You can then search this document or generate content from it from the Document Search or Content Generator menu areas
6. If you wish to add another documents to the group, navigate to the Document Manager section and select the group you want to add it and upload as usual
7. You can add as many documents or document groups as you wish

## Contributing

Contributors are always welcome to Local Rag. I appreciate any input that aids in improving this project. Anyone interested in making a contribution may pull a request. 

## License

Local Rag is licensed under the open-source license.
