import re
import streamlit as st
from llm_response import generate_response
from api_validator import validate_api_call, attempt_to_fix_api_call

# Streamlit UI
st.set_page_config(page_title="API Chatbot", layout="wide")
st.title("Crustdata API Chatbot")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

def process_api_request(response):
    if extract_api_example(response) == None:
        return response
    
    results = extract_api_example(response)
    for result in results:
        lang = result['language']
        api_example = result['code']
        start_idx = result['start_idx']
        end_idx = result['end_idx']  

        # Show a pop-up-like message while validating the code block
        with st.spinner("Bot response contains some executables. Verifying them for you..."):
            validation_result, error_log = validate_api_call(api_example)

            if validation_result:
                continue  # API call is valid, return original response
            else:
                # Attempt to fix the API call using error logs
                complete_api_example = f"```{lang}\n{api_example}```"
                fixed_api_example = attempt_to_fix_api_call(complete_api_example, error_log)
                fixed_api_example = "```" + re.search(r"```(.*?)```", fixed_api_example, re.DOTALL).group(1) + "```"
                response = response[:start_idx] + fixed_api_example + response[end_idx + 1:]
    return response

def extract_api_example(response):
    if "```" in response: 
        # Match code blocks enclosed in ``` followed by a language identifier
        pattern = r"```(.*?)\n(.*?)```"
        matches = list(re.finditer(pattern, response, re.DOTALL))

        results = []
        for match in matches:
            language = match.group(1).strip()  # Capture the language (e.g., python)
            code = match.group(2)             # Capture the code inside
            start_idx, end_idx = match.span() # Get the start and end indices
            results.append({
                "language": language,
                "code": code,
                "start_idx": start_idx,
                "end_idx": end_idx
            })

        return results
    return None

# Display chat history (if any)
if st.session_state.history:
    for chat in st.session_state.history:
        with st.container():
            st.markdown(f"**You:** {chat['user']}")
            st.markdown(f"**Bot:** {chat['bot']}")
            st.markdown("---")

# Input section
with st.container():
    if not st.session_state.history:  # If no history, show input at the top
        st.markdown("---")
    user_input = st.text_input(
        "Ask a question about Crustdata's APIs:", 
        key="user_input", 
        value=""  # Ensures the input box is cleared after submission
    )

    if st.button("Submit"):
        if user_input.strip():  # Ensure input is not empty
            # Generate response
            response = generate_response(user_input)

            # Validate the response
            response = process_api_request(response)

            # Save question and answer to history
            st.session_state.history.append({"user": user_input, "bot": response})

            # Clear the input box
            st.rerun()
