# Various Imports
import os
import sys
import shutil

import gradio as gr

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores.chroma import Chroma
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain # conversational for memory

# OpenAI API Key -- replace "..." with key
os.environ["OPENAI_API_KEY"] = "..."

# Directory from which to pull documents
directory_str = "/Users/Vuk/Desktop/Take Home/Documents"
documents_directory = os.fsencode(directory_str)
# Add directory to path
p = Path(directory_str)
# Directory to store persistent vector embeddings (PVE)
vector_storage = "/Users/Vuk/Desktop/Take Home Code/persist_dir"

# When True, vector database will always be regenerated
override = True

# Function to check if a PVE storage exists at a given directory path
def exists(vector_storage_path):
    if os.path.exists(vector_storage_path):
        return True
    else:
        return False

# Function to create a PVE at a given directory path (vector_storage_path), using documents found in the other (d_directory)
def make_vector_storage(vector_storage_path, d_directory):
    print("[+] GENERATING VECTOR EMBEDDINGS")
    # List of all documents in the location
    docs = []

    # Loop through all files in the documents directory
    for file in os.listdir(d_directory):
        # Encode each file
        filename = os.fsdecode(file)
        # Create the full file path, handle occasional "\" character
        file_path = os.path.join(p, filename).replace("\\", "/")
        # Create PyPDFLoader
        loader = PyPDFLoader(file_path)
        # Load the document into a list
        documents = loader.load()
        # Add the document to the previous list
        docs.extend(documents)

    # Recursively split the text from all of the documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)
    # Create a Chroma storage space for the vector embeddings from the documents
    vector_db = Chroma.from_documents(docs, embedding=OpenAIEmbeddings(), persist_directory=vector_storage_path)
    # Push to the PVE storage
    vector_db.persist()
    # Return the vector database
    return vector_db

# Function to delete an existing PVE at a given directory path (vector_storage_path)
def delete_vector_storage(vector_storage_path):
    print("[-] REMOVING VECTOR STORAGE")
    try:
        shutil.rmtree(vector_storage_path)
        print("Directory removed successfully")
    except FileNotFoundError:
        print("Directory does not exist")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# If block to handle cases for the existence and override logic for the PVE storage
if override:
    if exists(vector_storage):
        # Override and already exists
        delete_vector_storage(vector_storage)

    vector_db = make_vector_storage(vector_storage, documents_directory)
else:
    if exists(vector_storage):
        # No override and exists
        print("[*] LOADING EXISTING STORAGE")
        vector_db = Chroma(persist_directory=vector_storage, embedding_function=OpenAIEmbeddings())
        pass
    else:
        # No override and does not exist
        vector_db = make_vector_storage(vector_storage, documents_directory)

# Create the conversational chain of the RAG, using the generated vector embeddings 
qa_chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.9, model_name="gpt-3.5-turbo"), vector_db.as_retriever(search_kwargs={'k': 5}), return_source_documents=False, verbose=False)

# UI blocks
with gr.Blocks() as demo:
    # Space for AI chatbot
    chatbot = gr.Chatbot(label="Aerospace Assistant")
    # Space for user input
    msg = gr.Textbox(label="Enter Questions Here")

    # Location to store the newly uploaded user file -- same location as all the other files

    # Function for uploading user files
    def upload_file(file):
        # Get a string of the user file, handle occasional "\"
        file_path = str(file).replace("\\", "/")[2:]
        # Copy the contents of the file from a temp folder (controlled by gradio) to the location we want
        shutil.copy(file_path, directory_str)
        # Remake the vector storage*
        vector_db = make_vector_storage(vector_storage, documents_directory)
        return file_path

    with gr.Row():
        # Clear button to wipe user textbox
        clear = gr.Button("Clear")
        
        # Allow the user to upload a file to the AI
        file_output = gr.File()
        # Note: only allows one file at a time
        upload_button = gr.UploadButton("Click to Upload a File", file_types=["file"], file_count="single")
        upload_button.upload(upload_file, upload_button, file_output)

        # Regenerate the AI
        qa_chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.9, model_name="gpt-3.5-turbo"), vector_db.as_retriever(search_kwargs={'k': 5}), return_source_documents=False, verbose=False)

    # List some examples to prompt users
    examples = gr.Examples(examples=["What are the steps in refueling without DC power?", "Where is the no smoking switch located?"], inputs=[msg])

    # List for storing conversational history between user and AI
    chat_history = []
    
    # Function for generating RAG responses
    def generate(user_message, history):
        # Get response from QA chain
        result = qa_chain.invoke({"question": user_message, "chat_history": chat_history})
        # Append user message and response to chat history
        chat_history.append((user_message, result["answer"]))
        # return resulting value and clear user textbox
        return gr.update(value=""), chat_history
    msg.submit(generate, [msg, chatbot], [msg, chatbot], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

# Create the webapp
demo.launch(debug=True) 