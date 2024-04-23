# Alwrity - AI LinkedIn Blog Post Generator

Alwrity is an AI-powered LinkedIn blog post generator designed to assist users in creating engaging and informative content for their LinkedIn profiles. This tool leverages AI technology to generate LinkedIn posts based on user-provided keywords and search results.

## Features

- **Persona Selection:** Choose from various types of LinkedIn posts, such as General, How-to Guides, Polls, Listicles, and more.
- **Input Section:** Provide main keywords, post type, post length, and language preferences to customize the generated LinkedIn post.
- **Post Generation:** Generate LinkedIn posts based on the provided inputs, including title, introduction, sections, FAQs, and conclusion.
- **Error Handling:** Handles exceptions gracefully and provides helpful error messages to users.
- **Progress Bar:** Displays a progress spinner during Google search and post generation to indicate activity.

## Usage

1. **Input Section:** Enter the main keywords of your post and select the post type, length, and language preferences.
2. **Generate LinkedIn Post:** Click the "Get LinkedIn Post" button to generate the LinkedIn post based on your inputs.
3. **View Post:** Once the post is generated, it will be displayed in the web app for you to review and use on LinkedIn.

## Requirements

- Python 3.6+
- Streamlit
- Tenacity
- Google Generative AI SDK

## How to Run

1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up environment variables:
   - `SERPER_API_KEY`: Serper API key for Google search.
   - `GEMINI_API_KEY`: Google Generative AI API key.
4. Run the Alwrity script using `streamlit run alwrity.py`.
