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
from exa_py import Exa


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

    serp_results = None
    try:
        serp_results = metaphor_search_articles(input_blog_keywords)
    except Exception as err:
        st.error(f"❌ Failed to retrieve search results for {input_blog_keywords}: {err}")

    # If keywords and content both are given.
    if serp_results:
        prompt = f"""As a expert and experienced linkedin content writer, 
        I will provide you with my 'blog keywords' and 'google search results'.
        Your task is to write a detailed linkedin post, using given keywords and search results.

        Follow below guidelines for generating the linkedin post:
        1). Write a title, introduction, sections, faqs and a conclusion for the post.
        2). Demostrate Experience, Expertise, Authoritativeness, and Trustworthiness with your post.
        3). Maintain consistent voice of tone, keep the sentence short and simple for professional audience.
        4). Make sure to include important results from the given google serp results.
        5). Optimise your response for blog type of {input_linkedin_type}.
        6). Important to provide your response in {input_linkedin_language} language.\n

        blog keywords: '{input_blog_keywords}'\n
        google serp results: '{serp_results}'
        """
        linkedin_post = generate_text_with_exception_handling(prompt)
        return linkedin_post


# Metaphor search function
def metaphor_search_articles(query):
    METAPHOR_API_KEY = os.getenv('METAPHOR_API_KEY')
    if not METAPHOR_API_KEY:
        raise ValueError("METAPHOR_API_KEY environment variable not set!")

    metaphor = Exa(METAPHOR_API_KEY)

    try:
        search_response = metaphor.search_and_contents(query, use_autoprompt=True, num_results=5)
        return search_response.results
    except Exception as err:
        st.error(f"Failed in metaphor.search_and_contents: {err}")
        return None


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
