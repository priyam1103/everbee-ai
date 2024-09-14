import random

def generate_html_page_one(navbar, content, prompt, generate_hero_image):
    # Extract values from JSON
    tagline = content["tagline"]
    cta = content["cta"]
    sections = content["sections"]
    theme = ["theme1", "theme2"]
    selected_theme = "theme1"

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

            if selected_theme == "theme1":
              html_sections += f"""
              <div class="hero">
                  <img src="{hero_image_path}" alt="Hero Banner Image">
                  <h1>{hero_tagline}</h1>
                  <a href="#" class="cta">{hero_cta}</a>
              </div>
              """
            else:
                html_sections += f"""
                <div class="hero-modern">
                    <div class="text-content">
                        <h1>{hero_tagline}</h1>
                        <a href="#" class="cta">{hero_cta}</a>
                    </div>
                    <div class="image-content">
                        <img src="{hero_image_path}" alt="Hero Image">
                    </div>
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
                font-family: font-family: 'Poppins', sans-serif;;
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
            .hero-modern {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 60px 20px;
                background-color: #f8f8f8; /* Optional background color */
            }}
            .hero-modern .text-content {{
                flex: 1;
                max-width: 600px;
            }}
            .hero-modern h1 {{
                font-size: 48px;
                margin-bottom: 20px;
                color: #333;
            }}
            .hero-modern .cta {{
                background-color: #ff6b6b;
                color: #fff;
                padding: 15px 30px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: bold;
                text-decoration: none;
                display: inline-block;
                transition: background-color 0.3s ease, color 0.3s ease;
            }}
            .hero-modern .cta:hover {{
                background-color: #e74c3c;
            }}
            .hero-modern .image-content {{
                flex: 1;
                text-align: center;
            }}
            .hero-modern .image-content img {{
                max-width: 75%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
