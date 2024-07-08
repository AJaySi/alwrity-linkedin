import time #Iwish
import os
import json
import requests
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import google.generativeai as genai


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity- AI linkedin Post writer",
        layout="wide",
    )
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
                ::-webkit-scrollbar-track {
        background: #e1ebf9;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9;
            border-radius: 10px;
            border: 3px solid #e1ebf9;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #64B5F6;
        }

        ::-webkit-scrollbar {
            width: 16px;
        }
        div.stButton > button:first-child {
            background: #1565C0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        }
        </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    # Title and description
    st.title("✍️ Alwrity - AI Linkedin Blog Post Generator")

    # Input section
    with st.expander("**💡 PRO-TIP** - Read the instructions below.", expanded=True):
        input_blog_keywords = st.text_input('**🔑 Enter main keywords of your Post!**', placeholder='E.g., Marketing Trends, Leadership Tips...')
        col1, col2, space, col3 = st.columns([5, 5, 0.5, 5])
        with col1:
            input_linkedin_type = st.selectbox('📝 **Post Type**', (
                'General', 'How-to Guides', 'Polls', 'Listicles', 
                'Reality check posts', 'Job Posts', 'FAQs', 'Checklists/Cheat Sheets'), index=0)
        with col2:
            input_linkedin_length = st.selectbox('📏 **Post Length**', ('1000 words', 'Long Form', 'Short form'), index=0)
        with col3:
            input_linkedin_language = st.selectbox('🌐 **Choose Language**', (
                'English', 'Vietnamese', 'Chinese', 'Hindi', 'Spanish'), index=0)
    
    # Generate Blog FAQ button
    if st.button('🚀 **Get LinkedIn Post**'):
        with st.spinner('🔄 Assigning AI professional to write your LinkedIn Post...'):
            if not input_blog_keywords:
                st.error('🚫 **Provide Inputs to generate LinkedIn Post. Keywords are required!**')
            else:
                linkedin_post = generate_linkedin_post(
                    input_blog_keywords, input_linkedin_type, 
                    input_linkedin_length, input_linkedin_language)
                if linkedin_post:
                    st.subheader('🎉 **Go Rule LinkedIn with this Blog Post!**')
                    st.write(linkedin_post)
                else:
                    st.error("💥 **Failed to generate LinkedIn Post. Please try again!**")

# Function to generate blog metadesc
def generate_linkedin_post(input_blog_keywords, input_linkedin_type, input_linkedin_length, input_linkedin_language):
    """ Function to call upon LLM to get the work done. """

    # Fetch SERP results & PAA questions for FAQ.
    serp_results, people_also_ask = get_serp_results(input_blog_keywords)

    # If keywords and content both are given.
    if serp_results:
        prompt = f"""As a SEO expert and experienced linkedin content writer, 
        I will provide you with my 'blog keywords' and 'google serp results'.
        Your task is to write a detailed linkedin post, using given keywords and search results.

        Follow below guidelines for generating the linkedin post:
        1). Write a title, introduction, sections, faqs and a conclusion for the post.
        2). Your FAQ should be based on 'People also ask' and 'Related Queries' from given serp results.
        3). Maintain consistent voice of tone, keep the sentence short and simple.
        4). Make sure to include important results from the given google serp results.
        5). Optimise your response for blog type of {input_linkedin_type}.
        6). Important to provide your response in {input_linkedin_language} language.\n

        blog keywords: '{input_blog_keywords}'\n
        google serp results: '{serp_results}'
        people_also_ask: '{people_also_ask}'
        """
        linkedin_post = generate_text_with_exception_handling(prompt)
        return linkedin_post


def get_serp_results(search_keywords):
    """ """
    serp_results = perform_serperdev_google_search(search_keywords)
    people_also_ask = [item.get("question") for item in serp_results.get("peopleAlsoAsk", [])]
    return serp_results, people_also_ask


def perform_serperdev_google_search(query):
    """
    Perform a Google search using the Serper API.

    Args:
        query (str): The search query.

    Returns:
        dict: The JSON response from the Serper API.
    """
    # Get the Serper API key from environment variables
    serper_api_key = os.getenv('SERPER_API_KEY')

    # Check if the API key is available
    if not serper_api_key:
        st.error("SERPER_API_KEY is missing. Set it in the .env file.")

    # Serper API endpoint URL
    url = "https://google.serper.dev/search"
    # FIXME: Expose options to end user. Request payload
    payload = json.dumps({
        "q": query,
        "gl": "in",
        "hl": "en",
        "num": 10,
        "autocorrect": True,
        "page": 1,
        "type": "search",
        "engine": "google"
    })

    # Request headers with API key
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    # Send a POST request to the Serper API with progress bar
    with st.spinner("Searching Google..."):
        response = requests.post(url, headers=headers, data=payload, stream=True)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}, {response.text}")



@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt):
    """
    Generates text using the Gemini model with exception handling.

    Args:
        api_key (str): Your Google Generative AI API key.
        prompt (str): The prompt for text generation.

    Returns:
        str: The generated text.
    """

    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text

    except Exception as e:
        st.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
