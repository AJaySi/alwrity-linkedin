import time #Iwish
import os
import json
import openai
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity",
        layout="wide",
        page_icon="img/logo.png"
    )
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"""
      <style>
      [class="st-emotion-cache-7ym5gk ef3psqc12"]{{
            display: inline-block;
            padding: 5px 20px;
            background-color: #4681f4;
            color: #FBFFFF;
            width: 300px;
            height: 35px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 8px;’
      }}
      </style>
    """
    , unsafe_allow_html=True)

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    # Sidebar input for OpenAI API Key
    openai_api_key = st.sidebar.text_input("**Enter OpenAI API Key(Optional)**", type="password")
    st.sidebar.image("img/alwrity.jpeg", use_column_width=True)
    st.sidebar.markdown(f"🧕 :red[Checkout Alwrity], complete **AI writer & Blogging solution**:[Alwrity](https://alwrity.netlify.app)")
    
    # Title and description
    st.title("✍️ Alwrity - AI Linkedin Blog Post Generator")
    with st.expander("How to Write **Great Instagram Captions** ? 📝❗"):
        st.markdown('''
            **Step 1: Input Keywords** 📝
                - Enter 2-3 main keywords defining your blog post.
                - Use the text input field provided.

            **Step 2: Choose Post Type** 📌
                - Select the type of post from options like General, How-to Guides, Polls, etc.
                - Utilize the dropdown menu to make your selection.

            **Step 3: Determine Post Length** 📏
                - Choose the desired length of your post: 1000 words, Long Form, or Short form.
                - Use the dropdown menu to select your preference.

            **Step 4: Select Language** 🌐
                - Pick the language for your post from options like English, Vietnamese, Chinese, etc.
                - Utilize the dropdown menu to make your selection.

            **Step 5: Generate LinkedIn Post** 🚀
                - Click on the "Get LinkedIn Post" button to generate your post.
                - Error messages will prompt if any inputs are missing.
                - Upon successful generation, the post will be displayed.
                - Copy the generated post from the provided code block for use on LinkedIn.
            ''')

    # Input section
    with st.expander("**PRO-TIP** - Read the instructions below.", expanded=True):
        input_blog_keywords = st.text_input('**Enter main keywords of your Post!** (2-3 words that defines your blog)')
        col1, col2, space, col3 = st.columns([5, 5, 0.5, 5])
        with col1:
            input_linkedin_type = st.selectbox('Post Type', ('General', 'How-to Guides', 'Polls', 'Listicles', 
                'Reality check posts', 'Job Posts', 'FAQs', 'Checklists/Cheat Sheets'), index=0)
        with col2:
            input_linkedin_length = st.selectbox('Post Length', ('1000 words', 'Long Form', 'Short form'), index=0)
        with col3:
            input_linkedin_language = st.selectbox('Choose Language', ('English', 'Vietnamese',
                'Chinese', 'Hindi', 'Spanish'), index=0)
        # Generate Blog FAQ button
        if st.button('**Get LinkedIn Post**'):
            with st.spinner():
                # Clicking without providing data, really ?
                if not input_blog_keywords:
                    st.error('** 🫣Provide Inputs to generate Blinkedin Post. Keywords, required!**')
                elif input_blog_keywords:
                    linkedin_post = generate_linkedin_post(input_blog_keywords, input_linkedin_type, 
                            input_linkedin_length, input_linkedin_language)
                    if linkedin_post:
                        st.subheader('**👩🔬👩Go Rule LinkedIn with this Blog Post!**')
                        st.write(linkedin_post)
                    else:
                        st.error("💥**Failed to generate linkedin Post. Please try again!**")

    data_oracle = import_json(r"lottie_files/manager_robo.json")
    st_lottie(data_oracle, height=600, key="linkedin")

    st.markdown('''
                *Generates SEO optimized Linkedin Posts - powered by AI (OpenAI GPT-3, Gemini Pro).
                Implemented by [Alwrity](https://alwrity.netlify.app).
                Alwrity will do web research for given keywords and base blog on web research.
                It will process all top google results and present unique blog post, for you.*
                ''')

    st.subheader('**👩🔬👩 How to Write Killer LinkedIn Posts ?**')
    st.markdown('''

        1. **Utilize Plain Text Posts:** Use plain text to ensure clarity and impact in your message.
        2. **Incorporate Emojis:** Enhance content digestibility and highlight ideas by incorporating emojis.
        3. **Craft Compelling Headlines:** Capture user attention with compelling headlines that draw readers in.
        4. **Start with a Story:** Create relatability and interest by beginning your post with a story.
        5. **Break Up Text:** Improve readability by breaking up text into single-sentence paragraphs.
        6. **Mention Connections or Influencers:** Broaden post visibility by mentioning connections or influencers.
        7. **Provide Specific Instructions and Ask Questions:** Encourage engagement by offering specific 
             instructions and asking thought-provoking questions.
        8. **Offer Intellectual Property:** Add value to the LinkedIn community by sharing intellectual property.
        9. **Add Relevant Hashtags:** Increase post reach by including relevant hashtags.
        10. **Avoid External Links:** Maintain engagement by avoiding external links within posts.
        11. **Schedule Posts:** Ensure consistent visibility and performance by scheduling posts.
        12. **Provide Examples of Post Ideas:** Offer examples such as personal stories, job postings, 
            polls, video stories, reality check posts, job announcements, and how-to guides.

        Additionally, the content emphasizes the importance of:
        - **Lowering the Reading Level:** Keep posts simple and easy to read, aiming for a grade 
            level below your audience's formal education.
        - **Finessing Your Opening Line:** Grab attention with an engaging opening sentence.
        - **Jumping on the Latest Bandwagon:** Experiment with new LinkedIn features and content types to increase organic reach.
        - **Adding Visual Interest:** Incorporate images, videos, or other visual content to enhance engagement.
        - **Writing for an Audience of One:** Tailor posts as if speaking directly to a specific individual 
            within your network, simplifying language and ensuring clarity.
        ''')


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
        linkedin_post = openai_chatgpt(prompt)
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
def openai_chatgpt(prompt, model="gpt-3.5-turbo-0125", temperature=0.2, max_tokens=500, top_p=0.9, n=3):
    """
    Wrapper function for OpenAI's ChatGPT completion.

    Args:
        prompt (str): The input text to generate completion for.
        model (str, optional): Model to be used for the completion. Defaults to "gpt-4-1106-preview".
        temperature (float, optional): Controls randomness. Lower values make responses more deterministic. Defaults to 0.2.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 8192.
        top_p (float, optional): Controls diversity. Defaults to 0.9.
        n (int, optional): Number of completions to generate. Defaults to 1.

    Returns:
        str: The generated text completion.

    Raises:
        SystemExit: If an API error, connection error, or rate limit error occurs.
    """
    # Wait for 10 seconds to comply with rate limits
    for _ in range(10):
        time.sleep(1)

    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=n,
            top_p=top_p
            # Additional parameters can be included here
        )
        return response.choices[0].message.content

    except openai.APIError as e:
        st.error(f"OpenAI API Error: {e}")
    except openai.APIConnectionError as e:
        st.error(f"Failed to connect to OpenAI API: {e}")
    except openai.RateLimitError as e:
        st.error(f"Rate limit exceeded on OpenAI API request: {e}")
    except Exception as err:
        st.error(f"OpenAI error: {err}")



# Function to import JSON data
def import_json(path):
    with open(path, "r", encoding="utf8", errors="ignore") as file:
        url = json.load(file)
        return url


if __name__ == "__main__":
    main()
