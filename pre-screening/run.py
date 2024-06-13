# importing necessary libraries
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
    from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
import json
import os
import uuid

# Job positions and their questions
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
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
    
    st.title("Job Pre-Screening Chatbot")

    # Step: Collect User Information
    st.header("User Information")
    user_name = st.text_input("Name")
    user_location = st.text_input("Where are you from?")
    job_looking_for = st.text_input("What job are you looking for?")

    if st.button("Submit User Information"):
        st.session_state['user_info'] = {
            "name": user_name,
            "location": user_location,
            "job_looking_for": job_looking_for
        }
        st.success("User information submitted!")

    if 'user_info' in st.session_state:
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
                
        # Initialize OpenAI API key
        openai.api_key = st.secrets["openai_key"]
        
        st.header("Chat here for more info 💬")

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Ask me questions about different job positions!"}
            ]

        @st.cache_resource(show_spinner=False)
        def load_data():
            with st.spinner("Loading and indexing the job description details – hang tight! This should take 1-2 minutes."):
                reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
                docs = reader.load_data()
                service_context = ServiceContext.from_defaults(
                    llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, 
                    system_prompt="You are an expert on the given Job Descriptions in the text file of the data directory for this company. Your job is to answer the questions by prospective candidates. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features.")
                )
                index = VectorStoreIndex.from_documents(docs, service_context=service_context)
                return index

        index = load_data()

        chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

        if prompt := st.chat_input("Your question"): 
            st.session_state.messages.append({"role": "user", "content": prompt})

        for message in st.session_state.messages: 
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_engine.chat(prompt)
                    st.write(response.response)
                    message = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(message)

        # Review section
        st.subheader("Review your experience")
        review_rating = st.slider("Rate your experience with the chatbot", 1, 5, 3)
        
        # Submit Review button placed after the chat input
        if st.button("Submit Review"):
            save_conversation(job_position, answers, st.session_state.messages, review_rating)
            st.success(f"Thank you for your review! You rated us {review_rating} out of 5.")

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
            st.error("You did not pass the pre-screening for Data Analyst, but you can talk to our bot for more relevant job positions.")

def save_conversation(job_position, answers, messages, review_rating):
    user_info = st.session_state['user_info']
    user_name = user_info.get("name", "unknown").replace(" ", "_")  # Replace spaces with underscores
    conversation = {
        "user_id": st.session_state['user_id'],
        "user_info": user_info,
        "job_position": job_position,
        "answers": answers,
        "messages": messages,
        "review_rating": review_rating
    }
    if not os.path.exists("conversations"):
        os.makedirs("conversations")
    with open(f"conversations/conversation_{user_name['user_id']}.json", "w") as f:
        json.dump(conversation, f)

if __name__ == "__main__":
    main()
