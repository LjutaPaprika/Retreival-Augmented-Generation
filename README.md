# Retreival-Augmented-Generation
This repository contains a Generative AI model with a Retrieval-based mechanism for improved content generation, using the OpenAI API. Provide a directory for documents to take in as well as a location to store vector embeddings.

---
Tasks:
1. Read the PDF, split it up into chunks and store them in a vector database. Use OpenAI’s
embedding model to generate the vector embeddings. Determine the best way to split the
document.
  - First the primary input file is split into sub-files
    - Each sub-file is approx. 100 pages, but this can be adjusted
    - The sub-files are put into a unique directory
    - This is all handled in pdf_splitter.py
  - Each file is then added to a documents list, which is fed into a Recursive Character Text Splitter
  - A Chroma database is created to store the vector embeddings which are created with OpenAI's embedding model
  - Finally, if the vector embeddings already exist, they will simply be loaded rather than regenerated on each run
  - This method is great because it chunks large pdfs into smaller ones to improve text splitting time, and if a section of the pdf is problematic (eg. corrupt) then that section will simply be skipped and the program can continue
  - A Recursive Character Text Splitter was used as it tries to keep all paragraphs, sentences then words together as long as possible, to maintain semantic similarity as best as possible
  - Loading the embeddings rather than recreating them each time dramatically speeds up the process

2. Set up a basic pipeline that allows the user to ask a question, finds relevant documents in the
vector database, uses this information to create the prompt sent to OpenAI, and returns the
response to the user. Note: A UI is not required here - getting user input and returning responses
through the command line is fine.
  - The model uses a Conversational Retrieval Chain from langchain
    - It takes a users current question and the chat history to generate a new question, which is used to grab relevant documents, which finally are passed to an LLM with the new question to create a response
  - Each time the user enters a question the chain is invoked to access the LLM and generate a reply
  - Conversational Retrieval Chain is good as it acts to refine the original question the user asked, use it to collect relevant documents and answer user questions quickly
  - It utilizes the vector embeddings easily to find similarity across documents

3. Test the implementation with a number of different questions about the aircraft to test its
abilities and limitations. What types of questions can be successfully and correctly answered?
Which ones does the implementation struggle with? Can you improve the model’s capability in
these failure cases?
  - The model works great for just about every text only question (ie. questions that rely solely on text fields)
  - It is able to answer questions regarding proximity and spacial context (eg. What switches are close to the NO SMOKING switch?)
  - It is able to answer questions to list items that are related to one another (eg. List all switches located on the front overhead panel.)
  - It is able to answer questions asking for a step-by-step process (eg. What are the steps for refueling without AC power?)
  - It is able to answer questions for summaries/key ideas (eg. summarize the purpose of battery chargers in detail)
  - It is able to answer follow-up questions (eg. What other switches are located in that area -- previous question being about a particular switch)
  - It is unable to answer questions that are related to graphs, images, or tables
    - This is likely due to the Recursive Character Text Splitter, it is not intended for use on those kinds of fields
    - could potentially mix between different corpus splitters to isolate and embed problematic fields separately
  - Wording questions properly is important as being too vague gives odd responses -- for example, the switch question, if phrased differently, results in some repetition as well as listing the modes of certain switches (ie. OFF, AUTO, ON)
  - One interesting point is that depending on the question, the response will include notes regarding assumptions, aircraft specifics, etc.
---
Bonus Tasks:
1. Modify the chatbot to include citations in its response, identifying which pages and/or sections
of the aircraft manual (if any) were used to answer a question.
  - Unable to complete
  - Due to the way the page numbering works (ie. chapter.section.page number -- 13.20.3) it was difficult to capture this information

2. Included in the take-home is a second document, a report describing the events of an aircraft
accident (AAR0102.pdf). Modify the chatbot to be able to answer questions related to this
accident in addition to its initial capabilities.
  - Using the UI (See below), an upload button is added
    - the user can add one document at a time to the model
  - the model takes the document, creates a copy in an Uploads folder, finds the vector embeddings, and adds them to the vector storage system
  - The user can then ask questions about the accident in addition to the manual
  - This process makes use of existing functionality (vector storage functions, UI, etc.) and repurposes them efficiently to add important functionality
    - The only thing that was added specifically for this step is a file copy function, as gradio (UI) stores uploaded files in a strange temp directory, which is hidden from users
    - Also, the uploads folder is accessed and vector embeddings are generated for each file the user uploads. This means for each upload everything (in that directory) is regenerated. Looking into a more efficient solution

3. Add support for memory - providing the LLM with knowledge about past messages in the
current conversation, so that the chatbot can answer follow-up questions.
  - the Conversational Retrieval Chain requires a chat history input (as mentioned in Task #2) -- it is a list containing tuples and is of the form [(user_msg_1, chat_rsp_1), (user_msg_2, chat_rsp_2), ...]
  - This allows for the model to take in the conversational history and combine it with the new user prompt before feeding it into the LLM
  - It maintains context and semantic understanding of previous interactions to reply with as relevant an answer as possible

4. Implement a basic web interface to the chatbot using Gradio (https://www.gradio.app/). This
library has a built-in chatbot interface that you can use for your UI
  - The web interface makes use of gradio blocks:
    - chatbot block: space for the AI and user chats, shows the message history in a similar format as a text conversation
    - msg block: space for the user to enter their questions
    - clear button: the user can press the button to wipe the user textbox and the chatbot box (erasing the displayed history)
    - file button and display: the user can press the button to upload a file to the AI model. The file is shown in the display once uploaded.
    - examples prompts: the very bottom of the UI shows some sample questions the user can click on to show how the model works
  - All this functionality is done using the simple gradio blocks structure and can easily be updated to add other functions or modified to be more user-friendly/intuitive
