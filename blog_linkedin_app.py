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
import clipboard


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity - AI LinkedIn Post Writer",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Global CSS styles for UI improvements
    st.markdown("""
        <style>
            body {
                background-color: #f0f2f6;
            }
            div.stButton > button:first-child {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            div.stButton > button:first-child:hover {
                background-color: #0056b3;
            }
            .reportview-container .markdown-text-container {
                font-family: 'Helvetica Neue', sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)

    # Hide top header and footer for a cleaner UI
    hide_elements = """
        <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_elements, unsafe_allow_html=True)

    # Title and description
    st.title("✍️ Alwrity - AI LinkedIn Post Generator")
    st.write("Leverage AI to craft high-quality LinkedIn posts tailored to your audience.")

    # Initialize session state for generated post
    if "linkedin_post" not in st.session_state:
        st.session_state.linkedin_post = ""

    # Input section with an informative expander
    with st.expander("💡 **PRO TIP** - Follow these instructions for better results.", expanded=True):
        st.write("1. Use specific keywords related to your topic.\n"
                 "2. Choose a post type that aligns with your message.\n"
                 "3. Select an appropriate language and length for your audience.")

        # Input fields for the LinkedIn post generator
        input_blog_keywords = st.text_input(
            '🔑 **Enter main keywords for your post**', 
            placeholder='e.g., Marketing Trends, Leadership Tips...', 
            help="Use relevant keywords that define the topic of your LinkedIn post."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            input_linkedin_type = st.selectbox('📝 **Post Type**', (
                'General', 'How-to Guides', 'Polls', 'Listicles', 
                'Reality Check Posts', 'Job Posts', 'FAQs', 'Checklists/Cheat Sheets'), 
                index=0, help="Choose the format that suits the message you want to deliver.")
        with col2:
            input_linkedin_length = st.selectbox('📏 **Post Length**', 
                ('1000 words', 'Long Form', 'Short Form'), index=0, 
                help="Decide the length of your post based on its complexity and target audience.")
        with col3:
            input_linkedin_language = st.selectbox('🌐 **Choose Language**', 
                ('English', 'Vietnamese', 'Chinese', 'Hindi', 'Spanish'), 
                index=0, help="Pick the language that resonates best with your audience.")

    # Button to generate the LinkedIn post
    if st.button('🚀 **Generate LinkedIn Post**'):
        if not input_blog_keywords:
            st.error('🚫 **Please provide keywords to generate a LinkedIn post!**')
        else:
            with st.spinner('🤖 Crafting your LinkedIn post...'):
                # Progress bar for user feedback
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.03)
                    progress_bar.progress(percent_complete + 1)

                # Generate the LinkedIn post
                st.session_state.linkedin_post = generate_linkedin_post(
                    input_blog_keywords, input_linkedin_type, 
                    input_linkedin_length, input_linkedin_language)

            # Post generation success message
            st.success('🎉 **Your LinkedIn post is ready!**')
            st.subheader('📄 **LinkedIn Post Preview**')
            st.write(st.session_state.linkedin_post)

            # Copy to Clipboard button with success feedback
            if st.button('📋 Copy to Clipboard'):
                clipboard.copy(st.session_state.linkedin_post)
                st.success("✅ LinkedIn post copied to clipboard!")


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
