import streamlit as st
from openai import OpenAI
import json
import requests
import os

client = OpenAI(
  organization=os.environ.get('ORG'),
  api_key=os.environ.get('KEY'),
)

# Step 4: Function to generate landing page content using OpenAI
def generate_landing_page_content(business_description):
    prompt = f"""
    You are a business consultant. Please return the following sections for a landing page for a business with this description:
    "{business_description}"

    Format your response in the following JSON structure:

    {{
        "tagline": "A short catchy tagline for the hero banner",
        "cta": "Call-to-action text",
        "services": [
            {{"title": "Service 1", "description": "Description of service 1"}},
            {{"title": "Service 2", "description": "Description of service 2"}},
            {{"title": "Service 3", "description": "Description of service 3"}}
        ],
        "products": [
            {{"name": "Product 1", "description": "Description of product 1"}},
            {{"name": "Product 2", "description": "Description of product 2"}},
            {{"name": "Product 3", "description": "Description of product 3"}}
        ],
        "reviews": [
            {{"review": "Customer review 1"}},
            {{"review": "Customer review 2"}}
        ],
        "shipping_and_delivery": [
            {{"title": "Service 1", "description": "Description of service 1"}},
            {{"title": "Service 2", "description": "Description of service 2"}},
            {{"title": "Service 3", "description": "Description of service 3"}}
        ],
    }}
    """

    response = client.chat.completions.create(
    model="gpt-4o-mini",  # Adjust the model based on your available options

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1500
)
    

    raw_response = response.choices[0].message.content.strip()
    print("Raw AI Response:")
    print(raw_response)

    # Clean up response to remove any code block markers (e.g., triple backticks)
    clean_response = raw_response.replace("```json", "").replace("```", "").strip()

    # Try to load the response as JSON
    try:
        print(json.loads(clean_response))
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def generate_hero_image(prompt_description):
    dalle_prompt = f"A hero banner image. Background should be soft and inviting, with vibrant color. Related to the business: {prompt_description}"
    
    # dalle_url = "https://api.openai.com/v1/images/generations"  # Replace with actual DALL-E endpoint if you're using one
    # dalle_payload = {"prompt": dalle_prompt, "size": "1024x1024"}  # Adjust parameters as needed
    
    # # Assuming you are using a DALL-E service that gives you an image URL, like OpenAI's image API
    # response = requests.post(dalle_url, json=dalle_payload)
    
    # if response.status_code == 200:
    #     return response.json()["data"][0]["url"]  # Replace with actual response structure
    # else:
    #     print("Error generating image")
    #     return None

    response = client.images.generate(
      model="dall-e-3",
      prompt=dalle_prompt,
      size="1792x1024",
      quality="standard",
      n=1,
    )

    image_url = response.data[0].url
    return image_url

# Step 5: Function to generate HTML using the AI-generated content and hero image
def generate_html_page(navbar, content, hero_image_path):
    # Extract values from JSON
    print(content)
    tagline = content["tagline"]
    cta = content["cta"]
    
    # Generate services section
    services = ''.join([f"<div class='service'><h3>{service['title']}</h3><p>{service['description']}</p></div>" for service in content["services"]])
    
    # Generate products section
    products = ''.join([f"<div class='product'><h3>{product['name']}</h3><p>{product['description']}</p></div>" for product in content["products"]])
    
    # Generate reviews section
    reviews = ''.join([f"<div class='review'><p>{review['review']}</p></div>" for review in content["reviews"]])
    
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
            .services, .products, .reviews {{
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
            }}
            .service, .product, .review {{
                background-color: #fff;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding: 25px;
                border-radius: 16px;
                width: 300px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                text-align: left;
            }}
            .service:hover, .product:hover, .review:hover {{
                transform: translateY(-10px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            }}
            .service h3, .product h3 {{
                margin-bottom: 15px;
                font-size: 22px;
                color: #ff6b6b;
            }}
            .footer {{
                background-color: #282828;
                color: white;
                text-align: center;
                padding: 20px;
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
            .feature-text h1 {{
                font-size: 2.5rem;
                color: #001e64;
                margin-bottom: 20px;
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
            
            .shipping-delivery-section {{
                background-color: #f4f4f4; /* Light background color */
                padding: 50px;
                border-radius: 12px;
                margin: 0 auto;
                text-align: center;
            }}

            .shipping-delivery-section h2 {{
                font-size: 2rem;
                margin-bottom: 30px;
                color: #333;
            }}

         
            .shipping-options-row {{
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
                margin: 15px;
            }}
            .option {{
                background-color: #fff;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 20px;
                width: 45%; /* Adjust width to fit two items per row */
                text-align: left;
            }}

            .option h3 {{
                font-size: 1.2rem;
                margin-bottom: 10px;
                color: #333;
            }}

            .option p {{
                font-size: 1rem;
                color: #555;
            }}

            .number-box {{
                display: inline-block;
                font-size: 1.2rem;
                font-weight: bold;
                color: #333;
                background-color: #f4f4f4;
                padding: 10px 20px;
                border-radius: 50%;
                margin-bottom: 15px;
            }}

        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav>
            {navbar}
        </nav>

        <!-- Hero Section -->
        <div class="hero">
            <img src="{hero_image_path}" alt="Hero Banner Image">
            <h1>{tagline}</h1>
            <a href="#" class="cta">{cta}</a>
        </div>

        <!-- Services Section -->
        <div class="section">
            <h2>Services We Offer</h2>
            <div class="services">
                {services}
            </div>
        </div>

         <section class="feature-section">
          <div class="feature-container">
            <div class="feature-text">
              <h1>{content["services"][0]['title']}</h1>
              <p>{content["services"][0]['description']}</p>
              <a href="#" class="learn-more">Learn more →</a>
            </div>
            <div class="feature-image">
              <img src="{hero_image_path}" alt="Feature Image" />
            </div>
          </div>
        </section>

        <!-- Featured Products Section -->
        <div class="section">
            <h2>Featured Products</h2>
            <div class="products">
                {products}
            </div>
        </div>

        <!-- Customer Reviews Section -->
        <div class="section">
            <h2>Customer Reviews</h2>
            <div class="reviews">
                {reviews}
            </div>
        </div>

        <div class="shipping-delivery-section">
            <h2>Shipping and Delivery Options</h2>
            <div class="shipping-options">
                <div class="shipping-options-row">

                <div class="option">
                    <div class="number-box">1</div>
                    <h3>{content["shipping_and_delivery"][0]['title']}</h3>
                    <p>{content["shipping_and_delivery"][0]['description']}</p>
                </div>
                <div class="option">
                    <div class="number-box">2</div>
                    <h3>{content["shipping_and_delivery"][1]['title']}</h3>
                    <p>{content["shipping_and_delivery"][1]['description']}</p>
                </div>
                </div>
                <div class="shipping-options-row">

                <div class="option">
                    <div class="number-box">3</div>
                    <h3>{content["shipping_and_delivery"][2]['title']}</h3>
                    <p>{content["shipping_and_delivery"][2]['description']}</p>
                </div>
                <div class="option">
                    <div class="number-box">3</div>
                    <h3>{content["shipping_and_delivery"][0]['title']}</h3>
                    <p>{content["shipping_and_delivery"][0]['description']}</p>
                </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Contact Us | Privacy Policy | Terms of Service</p>
        </div>
    </body>
    </html>
    """
    return html_template

# Step 6: Main function to handle user input and generate the page
def generate_landing_page_content_data(prompt):
    # Get user input for the business description
    # business_description = input("Enter a description of your business: ")
    
    # Generate landing page content in JSON format
    # prompt = "Create engaging content for a modern home decor and furniture store that offers eco-friendly and sustainable products. The store features a wide range of stylish furniture, lighting, and accessories designed for a contemporary home. Emphasize eco-conscious values, craftsmanship, and any special offers for first-time buyers."   
    content = generate_landing_page_content(prompt)    
    hero_image_path = generate_hero_image(prompt)
    print(hero_image_path)
    # Navbar (static for now, you can add logic to generate dynamic items)
    navbar = '<a href="#">Home</a> <a href="#">Services</a> <a href="#">Products</a> <a href="#">Contact Us</a>'
    
    # Hero image path (you can save or display the image)
    # hero_image_path = "https://i.etsystatic.com/isbl/f8df64/62802669/isbl_3360x840.62802669_bfromjai.jpg?version=0"
    
    # Generate HTML
    html_page = generate_html_page(navbar, content, hero_image_path)
    
    # Save the HTML to a file
    # with open("landing_page_with_image.html", "w") as file:
    #     file.write(html_page)
    
    print("\nYour landing page with a hero image has been generated and saved as 'landing_page_with_image.html'.")
    return html_page


# Streamlit UI
st.title("E-Commerce Landing Page Generator")

# User input prompt
user_prompt = st.text_area("Enter your prompt for the eCommerce landing page:", "")

if st.button("Generate Page"):
    if user_prompt:
        with st.spinner("Generating landing page content..."):
            content = generate_landing_page_content_data(user_prompt)
            if content:
                html_output = content
                
                # Display HTML as iframe in Streamlit
                st.components.v1.html(html_output, height=600, scrolling=True)
            else:
                st.error("Failed to generate content. Please try again.")
    else:
        st.warning("Please enter a prompt to generate the landing page.")


