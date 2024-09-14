import streamlit as st
from openai import OpenAI
import json
import requests
import os
from gen_html_one import generate_html_page_one
from gen_html_two import generate_html_page_two
import random
import time

client = OpenAI(
  organization=os.environ.get('ORG'),
  api_key=os.environ.get('KEY'),
)

def generate_sitemap(prompt):
    sitemap_prompt = f"""
    I want you to create a JSON sitemap for a landing page (homepage) for this ecommerce business: {prompt}.
    The sitemap should include the following section types in any order - mix three_point_description and  text_image_section:
    - 'hero_banner' for the hero section with a catchy tagline and call-to-action
    - 'three_point_description' for sections that summarize information using three key points (e.g., services, featured products, features). There can be multiple sections of this type.
    - 'text_image_section' for sections that have text on the left and an image on the right. There can be multiple sections of this type.
    
    Each section should include:
    - A 'name' field that specifies the name of section
    - A 'description' field that provides a brief description of what content should go in that section.
    - A category - (e.g., 'hero_banner', 'three_point_description', or 'text_image_section')
    
    At least 6 sections - 

    Ensure the output is in this exact JSON format, with multiple sections allowed, alternate 'three_point_description' and 'text_image_section':

    {{
      "sections": [
        {{
          "name": "",
          "description": "",
          "category":""

        }},
      ]
    }}
    
    Please ensure the JSON output follows this structure exactly.
    """



    response = client.chat.completions.create(
    model="gpt-4o-mini",  # Adjust the model based on your available options

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": sitemap_prompt}
    ],
    max_tokens=1500
   )
    
    raw_sitemap = response.choices[0].message.content.strip()
    # Clean up response to remove any code block markers (e.g., triple backticks)
    clean_response = raw_sitemap.replace("```json", "").replace("```", "").strip()
    # Try to load the response as JSON
    print(clean_response)
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def generate_landing_page_content(business_description, sitemap):
    # Create a detailed prompt based on the sitemap
    prompt = f"""
    You are a professional landing page content generator. Please create content for a business with this description:
    "{business_description}"

    The landing page structure is provided in the sitemap below. Please generate content for each section type in the format specified.

    Section types:
    - **hero_banner**: Provide a short, catchy tagline and a call-to-action button text.
    - **three_point_description**: Generate three key points. Each point should include a title and a short description.
    - **text_image_section**: Provide text content for the left side, a call-to-action button text, and a URL for an image to be displayed on the right.

    The response must follow this JSON structure:

    {{
        "tagline": "A short catchy tagline for the hero banner",
        "cta": "Call-to-action text",
        "sections": [
            {{
                "type": "section type from sitemap",
                "name:: "name of section",
                "content": {{
                    "tagline": "Generated tagline for hero banner" OR
                    "points": [
                        {{"title": "Title 1", "description": "Description 1"}},
                        {{"title": "Title 2", "description": "Description 2"}},
                        {{"title": "Title 3", "description": "Description 3"}}
                    ] OR
                    "text": "Generated text for left side",
                    "cta": "Call-to-action button text",
                    "image_url": "https://example.com/placeholder.jpg"
                }}
            }},
            ...additional sections...
        ]
    }}

    Sitemap to process:

    {json.dumps(sitemap, indent=4)}

    Please ensure that each section in the sitemap is processed according to its type, with generated content inserted into the appropriate fields.
    """

    response = client.chat.completions.create(
    model="gpt-4o-mini",  # Adjust the model based on your available options

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=2000,
    temperature= 0.7
    )
    
    raw_response = response.choices[0].message.content.strip()

    # Clean up response to remove any code block markers (e.g., triple backticks)
    clean_response = raw_response.replace("```json", "").replace("```", "").strip()
    print(clean_response)
    # Try to load the response as JSON
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def generate_hero_image(prompt_description, description = "hero_banner"):
    dalle_prompt = f"A hero banner image. Background should be soft and inviting, with vibrant color. Related to the business: {prompt_description} and for section {description}"
    
    response = client.images.generate(
      model="dall-e-3",
      prompt=dalle_prompt,
      size="1792x1024",
      quality="standard",
      n=1,
    )

    image_url = response.data[0].url
    return image_url

# Step 6: Main function to handle user input and generate the page
def generate_landing_page_content_data(prompt, site_map, theme):
    # Get user input for the business description
    # business_description = input("Enter a description of your business: ")
    
    # Generate landing page content in JSON format
    # prompt = "Create engaging content for a modern home decor and furniture store that offers eco-friendly and sustainable products. The store features a wide range of stylish furniture, lighting, and accessories designed for a contemporary home. Emphasize eco-conscious values, craftsmanship, and any special offers for first-time buyers."   
    content = generate_landing_page_content(prompt, site_map)    
    # Navbar (static for now, you can add logic to generate dynamic items)
    navbar = '<a href="#">Home</a> <a href="#">Services</a> <a href="#">Products</a> <a href="#">Contact Us</a>'
    
    # Hero image path (you can save or display the image)
    # hero_image_path = "https://i.etsystatic.com/isbl/f8df64/62802669/isbl_3360x840.62802669_bfromjai.jpg?version=0"
    
    # Generate HTML
    selected_theme = theme
    html_page = generate_html_page_one(navbar, content, prompt, generate_hero_image) if selected_theme == "theme1" else generate_html_page_two(navbar, content, prompt, generate_hero_image)
    
    # Save the HTML to a file
    # with open("landing_page_with_image.html", "w") as file:
    #     file.write(html_page)
    
    print("\nYour landing page with a hero image has been generated and saved as 'landing_page_with_image.html'.")
    return html_page

def load_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_sitemap_ui(site_map):
    """
    Generates an HTML representation of the sitemap for visual display in Streamlit with a delay to simulate real-time generation.
    """
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Sitemap</h2>", unsafe_allow_html=True)
    
    for section in site_map['sections']:
        section_name = section['name']
        section_description = section['description']
        section_category = section['category']
        
        # Use st.empty to create a placeholder that will be updated
        placeholder = st.empty()

        # Update the placeholder with the new section HTML
        placeholder.markdown(f"""
        <div>
            <h3 style="color: #007BFF;">{section_name}</h3>
            <p><strong>Category:</strong> {section_category}</p>
            <p>{section_description}</p>
        </div>
        """, unsafe_allow_html=True)

        # Introduce a delay of 1 second before the next section
        time.sleep(0.5)

# Adding Everbee logo (replace 'everbee_logo.png' with the actual file path or URL)
st.image("https://everbee.io/wp-content/uploads/2024/05/Everbee-Logo.svg", width=150)

# App title with Everbee branding
st.title("Everbee E-Commerce Site Generator")

# User input prompt
user_prompt = st.text_area("Enter your prompt to generate an eCommerce landing page:", "")

# Scroll down JavaScript code
scroll_js = """
<script>
    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
</script>
"""



# Check if the sitemap has been generated
if 'site_map' not in st.session_state:
    st.session_state['site_map'] = None

# Check if the theme is selected
if 'selected_theme' not in st.session_state:
    st.session_state['selected_theme'] = None

# Step 2: Generate the sitemap based on user input
if st.button("Generate Sitemap"):
    if user_prompt:
        with st.spinner("Generating site map..."):
            site_map = generate_sitemap(user_prompt)
            st.session_state['site_map'] = site_map
            if site_map:
                generate_sitemap_ui(site_map)
            else:
                st.error("Failed to generate the sitemap. Please try again.")
    else:
        st.warning("Please enter content to generate the sitemap.")

# Step 3: If the sitemap is generated, let the user choose a theme
if st.session_state['site_map']:
    st.subheader("Select a theme for your landing page")

    # Load theme previews (simulating loading HTML from external files)
    theme_one_html = load_html_file('theme1.html')
    theme_two_html = load_html_file('theme2.html')

    # Display both theme previews as HTML
    st.components.v1.html(theme_one_html, height=300, width=1000, scrolling=True)
    st.components.v1.html(theme_two_html, height=300, width=1000, scrolling=True)

    # Let the user select a theme
    selected_theme = st.radio("Choose a theme:", ["Select a theme", "Theme1", "Theme2"])

    # Store the selected theme in session state
    if selected_theme != "Select a theme":
        st.session_state['selected_theme'] = selected_theme
    else:
        st.warning("Please select a theme to proceed.")

# Step 4: If a theme is selected, allow the user to generate the landing page
if st.session_state['selected_theme']:
    with st.spinner("Generating landing page..."):
        # Generate content based on the selected theme
        content = generate_landing_page_content_data(user_prompt, st.session_state['site_map'], theme=st.session_state['selected_theme'].lower())

        # Check if the content was successfully generated
        if content:
            html_output = content
            # Display HTML as an iframe in Streamlit
            st.components.v1.html(html_output, height=1000, width=1100, scrolling=True)
        else:
            st.error("Failed to generate content. Please try again.")



# if st.button("Publish"):
#     # Save HTML to a file
#     file_name = "index.html"
#     with open(file_name, "w") as file:
#         file.write(html_output)

#     # Step 2: Set up Netlify API details
#     netlify_token = "your_netlify_personal_access_token"  # Replace with your Netlify token

#     # API headers
#     headers = {
#         "Authorization": f"Bearer nfp_tHUp127t9CHRWKubPYoQsL5sfQDWXPkXaf4b",
#         "Content-Type": "application/json"
#     }

#     # Step 3: Create a new site on Netlify
#     create_site_url = "https://api.netlify.com/api/v1/sites"
#     response = requests.post(create_site_url, headers=headers)

#     if response.status_code == 200:
#         site_info = response.json()
#         new_site_id = site_info["site_id"]
#         new_site_url = site_info["url"]

#         print(f"New site created with ID: {new_site_id}")
#         print(f"Site URL: {new_site_url}")

#         # Step 4: Deploy HTML content to the new site
#         deploy_url = f"https://api.netlify.com/api/v1/sites/{new_site_id}/deploys"
        
#         # Read the HTML file as binary to upload
#         with open(file_name, "rb") as file:
#             files = {
#                 'files': (file_name, file, 'text/html')
#             }
#             deploy_response = requests.post(deploy_url, headers=headers, files=files)

#         if deploy_response.status_code == 200:
#             print(f"HTML deployed successfully! Your site is live at {new_site_url}")
#         else:
#             print(f"Failed to deploy HTML: {deploy_response.status_code} - {deploy_response.text}")
#     else:
#         print(f"Failed to create site: {response.status_code} - {response.text}")
    

# # Generate button and logic
# if st.button("Generate Page"):
#     if user_prompt:
#         with st.spinner("Generating site map..."):
#             site_map = generate_sitemap(user_prompt)
#             if site_map:
#                 generate_sitemap_ui(site_map)
#             else:
#                 st.error("Failed to generate content. Please try again.")

#         # Add JS for smooth scrolling (placeholder)
#         scroll_js = "<script>/* Add smooth scrolling */</script>"
#         st.markdown(scroll_js, unsafe_allow_html=True)

#         st.subheader("Select a theme for your landing page")

#         # Load theme previews
#         theme_one_html = load_html_file('theme1.html')
#         theme_two_html = load_html_file('theme2.html')

#         # Display both theme previews as HTML
#         st.components.v1.html(theme_one_html, height=300, width=1000, scrolling=True)
#         st.components.v1.html(theme_two_html, height=300, width=1000, scrolling=True)

#         # Let the user select a theme
#         selected_theme = st.radio("Choose a theme:", ("Select a theme", "Theme 1", "Theme 2"))

#         if selected_theme == "Select a theme":
#             st.warning("Please select a theme to proceed.")
#         else:
#             with st.spinner("Generating landing page..."):
#                 # Generate content based on the selected theme
#                 content = generate_landing_page_content_data(user_prompt, site_map, theme=selected_theme.lower())

#                 # Check if the content was successfully generated
#                 if content:
#                     html_output = content
#                     # Display HTML as an iframe in Streamlit
#                     st.components.v1.html(html_output, height=1000, width=1100, scrolling=True)
#                 else:
#                     st.error("Failed to generate content. Please try again.")
#     else:
#         st.warning("Please enter a prompt to generate the landing page.")


