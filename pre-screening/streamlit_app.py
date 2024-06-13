# importing necessary libraries. 

import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
    from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
import os

# generic questions 

job_positions = {
    "Software Engineer": [
        "Do you have a degree in Computer Science?",
        "Do you have experience with Python?",
        "Do you know data structures and algorithms?"
    ],
    "Data Analyst": [
        "Do you have experience with SQL?",
        "Do you know how to use Excel?",
        "Have you worked with data visualization tools?"
    ]
}

def main():
    st.title("Job Pre-Screening Chatbot")
    
    # Step 1: Select Job Position
    st.header("Step 1: Choose a Job Position")
    job_position = st.selectbox("Select a job position:", list(job_positions.keys()))
    
    if job_position:
        st.header(f"Step 2: Answer the Questions for {job_position}")
        
        # Step 2: Display Questions for the Selected Job Position
        answers = {}
        questions = job_positions[job_position]
        
        for question in questions:
            answer = st.selectbox(question, ["Yes", "No"], key=question)
            answers[question] = answer
        
        # Step 3: Evaluate Answers
        if st.button("Submit"):
            evaluate_answers(job_position, answers)
            
def evaluate_answers(job_position, answers):
    if job_position == "Software Engineer":
        if answers["Do you have a degree in Computer Science?"] == "Yes" and \
           answers["Do you have experience with Python?"] == "Yes" and \
           answers["Do you know data structures and algorithms?"] == "Yes":
            st.success("You passed the pre-screening for Software Engineer!")
        else:
            st.error("You did not pass the pre-screening for Software Engineer, but you can talk to our bot for more relevant job positions.")
    
    elif job_position == "Data Analyst":
        if answers["Do you have experience with SQL?"] == "Yes" and \
           answers["Do you know how to use Excel?"] == "Yes" and \
           answers["Have you worked with data visualization tools?"] == "Yes":
            st.success("You passed the pre-screening for Data Analyst!")
        else:
            st.error("You did not pass the pre-screening for Software Engineer, but you can talk to our bot for more relevant job positions.")
            
if __name__ == "__main__":
    main()


openai.api_key = st.secrets.openai_key
st.header("Chat with the this Pre-Screening Chatbot 💬")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about different job position!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the the job description details – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the given Job Descriptions in the text file of the data directory for this company. Your job is to answer the questions by prospective candidates. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
        
            st.session_state.messages.append(message) # Add response to message history

