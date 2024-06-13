import streamlit as st

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
            st.error("You did not pass the pre-screening for Software Engineer.")
    
    elif job_position == "Data Analyst":
        if answers["Do you have experience with SQL?"] == "Yes" and \
           answers["Do you know how to use Excel?"] == "Yes" and \
           answers["Have you worked with data visualization tools?"] == "Yes":
            st.success("You passed the pre-screening for Data Analyst!")
        else:
            st.error("You did not pass the pre-screening for Data Analyst.")
            
if __name__ == "__main__":
    main()
