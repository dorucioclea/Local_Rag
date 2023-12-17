# Local Rag

Local Rag is a fully local Retrieval Augmented Generation (RAG) system that uses Streamlit as the front end, Ollama and Transformers for the inference and Supabase for the database. This project offers an efficient, local, and private RAG system. It is specifically designed to query single or multuple documents held inside named groups, so groups of PDF/txt/docx in a specific catagory for example. Following this, it is easy to add new groups or add to existing groups. When the sources are retireved and processed, the AI output is supplied with the included sources.

In addition, two advanced RAG features are included, small-to-big document chunking and retrieval re-ranking.

Local Rag offers two outputs based on your query, document question answering and the ability to generate a post/conent based on your search query on the documents.

## Description

**Features**
- Select your LLM model for any models on Ollama
- Simple document chunking. This chunks the sources and embeds the chunk, upon retrieval the entire embedded chunk is used for synthesis
- Transformers is used for embedding and retrieval re-ranking
- Query your named doucment group with a question
- Query your named document group with a topic to write a post on
- Shows sources for retrieval
- Fully local with Ollama and Transformers
- Embeddings are done in batches of n size, this can be chosen based on your GPU, the default is 64
- The database is free for anyone and is hosted by Supabase
- Handle multiple document groups
- Easily add more documents to a current document group
- At the moment the chat history ins't used or remembered

**Advanced Features**
- Small-to-big chunking: The source is broken in sentences which are embedded, the surrounding paragraph is then stored for retrieval when the corresponding embedding is retrieved
- Retrieval re-ranking of the sources using the 'BAAI/bge-reranker-large' model. K x 4 sources are retrieved and ranked, then the new top k sources are chosen

**Future Features**
- Enable chat with conversation history as additiona context

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
6. Sign up for a free Supabase account, set up your database to populate the .yaml file
   ```markdown
   database_name:
   user:
   password:
   host:
   db_port:
   ```
7. Modify the .yaml file with your Supabase database and other relevant details.

## Usage

The Local Rag project is designed with a user-friendly interface and easy maneuvering. Once you've successfully followed the setup and installation steps, you can start using it for your document management. 

The system's document handling feature enables you to deal with multiple documents. You can add more documents and even more content to your existing documents. The project is designed with scalability and functionality in mind.

## Contributing

Contributors are always welcome to Local Rag. I appreciate any input that aids in improving this project. Anyone interested in making a contribution may pull a request. 

## License

Local Rag is licensed under the open-source license.
