import streamlit as st
from openai import OpenAI
import json
import requests
import os

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


def generate_html_page(navbar, content, prompt):
    # Extract values from JSON
    tagline = content["tagline"]
    cta = content["cta"]
    sections = content["sections"]

    # Initialize sections
    html_sections = ""
    image_section = 1  # To alternate between text-left and image-left

    # Loop through sections and generate the corresponding HTML
    for section in sections:
        section_type = section["type"]

        if section_type == "hero_banner":
            hero_tagline = section["content"]["tagline"]
            hero_cta = section["content"]["cta"]
            hero_image_path = generate_hero_image(prompt)  # Placeholder for the hero image
            html_sections += f"""
            <div class="hero">
                <img src="{hero_image_path}" alt="Hero Banner Image">
                <h1>{hero_tagline}</h1>
                <a href="#" class="cta">{hero_cta}</a>
            </div>
            """

        elif section_type == "three_point_description":
            points = section["content"]["points"]
            name = section["name"]
            points_html = ''.join([f"<div class='service'><h3>{point['title']}</h3><p>{point['description']}</p></div>" for point in points])
            html_sections += f"""
            <div class="section">
                <h2>{name}</h2>
                <div class="services">
                    {points_html}
                </div>
            </div>
            """

        elif section_type == "text_image_section":
            text = section["content"]["text"]
            cta_text = section["content"]["cta"]
            image_url = generate_hero_image(prompt, text)  # Placeholder for the feature image

            if image_section == 1:
                # Text on the left, image on the right
                html_sections += f"""
                <section class="feature-section">
                  <div class="feature-container">
                    <div class="feature-text">
                      <p>{text}</p>
                      <a href="#" class="learn-more">{cta_text}</a>
                    </div>
                    <div class="feature-image">
                      <img src="{image_url}" alt="Feature Image" />
                    </div>
                  </div>
                </section>
                """
                image_section = 0  # Toggle to show image on the left next
            else:
                # Image on the left, text on the right
                html_sections += f"""
                <section class="feature-section">
                  <div class="feature-container">
                    <div class="feature-image">
                      <img src="{image_url}" alt="Feature Image" />
                    </div>
                    <div class="feature-text">
                      <p>{text}</p>
                      <a href="#" class="learn-more">{cta_text}</a>
                    </div>
                  </div>
                </section>
                """
                image_section = 1  # Toggle to show text on the left next


    # Generate the final HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Business Landing Page</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f8f8;
                color: #333;
            }}
            nav {{
                background-color: #282828;
                padding: 20px;
                display: flex;
                justify-content: center;
            }}
            nav a {{
                color: white;
                margin: 0 20px;
                text-decoration: none;
                font-size: 16px;
                transition: color 0.3s ease;
            }}
            nav a:hover {{
                color: #ff6b6b;
            }}
            .hero {{
                color: white;
                text-align: center;
                padding: 100px 20px;
                position: relative;
                overflow: hidden;
            }}
            .hero img {{
                width: 100%;
                height: auto;
                opacity: 0.3;
                position: absolute;
                top: 0;
                left: 0;
                z-index: -1;
            }}
            .hero h1 {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .cta {{
                background-color: #fff;
                color: #ff6b6b;
                padding: 15px 30px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: bold;
                text-decoration: none;
                display: inline-block;
                transition: background-color 0.3s ease, color 0.3s ease;
            }}
            .cta:hover {{
                background-color: #ff6b6b;
                color: #fff;
                cursor: pointer;
            }}
            .section {{
                margin: 60px 0;
                text-align: center;
            }}
            .section h2 {{
                font-size: 32px;
                margin-bottom: 40px;
                color: #333;
            }}
            .services {{
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
            }}
            .service {{
                background-color: #fff;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding: 25px;
                border-radius: 16px;
                width: 300px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                text-align: left;
            }}
            .service:hover {{
                transform: translateY(-10px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            }}
            .service h3 {{
                margin-bottom: 15px;
                font-size: 22px;
                color: #ff6b6b;
            }}
            .feature-section {{
                background-color: #f0f2ff;
                padding: 50px 0;
            }}
            .feature-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                flex-wrap: wrap;
            }}
            .feature-text {{
                flex: 1;
                padding: 20px;
            }}
            .feature-text p {{
                font-size: 1.2rem;
                color: #5f5f6f;
                margin-bottom: 20px;
            }}
            .learn-more {{
                font-size: 1.1rem;
                color: #ff6a00;
                text-decoration: none;
                font-weight: bold;
            }}
            .feature-image {{
                flex: 1;
                text-align: right;
            }}
            .feature-image img {{
                max-width: 100%;
                height: auto;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            .footer {{
                background-color: #282828;
                color: white;
                text-align: center;
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav>
            {navbar}
        </nav>

        <!-- Dynamic Sections -->
        {html_sections}

        <!-- Footer -->
        <div class="footer">
            <p>Contact Us | Privacy Policy | Terms of Service</p>
        </div>
    </body>
    </html>
    """
    return html_template


# Step 6: Main function to handle user input and generate the page
def generate_landing_page_content_data(prompt, site_map):
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
    html_page = generate_html_page(navbar, content, prompt)
    
    # Save the HTML to a file
    # with open("landing_page_with_image.html", "w") as file:
    #     file.write(html_page)
    
    print("\nYour landing page with a hero image has been generated and saved as 'landing_page_with_image.html'.")
    return html_page


def generate_sitemap_ui(site_map):
    """
    Generates an HTML representation of the sitemap for visual display in Streamlit.
    """
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Sitemap</h2>", unsafe_allow_html=True)
    
    for section in site_map['sections']:
        section_name = section['name']
        section_description = section['description']
        section_category = section['category']
        
        st.markdown(f"""
        <div">
            <h3 style="color: #007BFF;">{section_name}</h3>
            <p><strong>Category:</strong> {section_category}</p>
            <p>{section_description}</p>
        </div>
        """, unsafe_allow_html=True)

# Adding Everbee logo (replace 'everbee_logo.png' with the actual file path or URL)
st.image("https://everbee.io/wp-content/uploads/2024/05/Everbee-Logo.svg", width=150)

# App title with Everbee branding
st.title("Everbee E-Commerce Site Generator")

# User input prompt
user_prompt = st.text_area("Enter your prompt to generate an eCommerce landing page:", "")

# Generate button and logic
if st.button("Generate Page"):
    if user_prompt:
        with st.spinner("Generating site map..."):
            site_map = generate_sitemap(user_prompt)
            if site_map:
                generate_sitemap_ui(site_map)
            else:
                st.error("Failed to generate content. Please try again.")
        with st.spinner("Generating landing page..."):
            content = generate_landing_page_content_data(user_prompt, site_map)
            if content:
                html_output = content
                
                # Display HTML as iframe in Streamlit
                st.components.v1.html(html_output, height=1000, width=1100, scrolling=True)
            else:
                st.error("Failed to generate content. Please try again.")
    else:
        st.warning("Please enter a prompt to generate the landing page.")



