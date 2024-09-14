import random


def generate_html_page_two(navbar, content, prompt, generate_hero_image):
    # Extract values from JSON
    tagline = content["tagline"]
    cta = content["cta"]
    sections = content["sections"]
    theme = ["theme1", "theme2"]
    selected_theme = random.choice(theme)

    # Initialize sections
    html_sections = ""
    image_section = 1  # To alternate between text-left and image-left

    # Loop through sections and generate the corresponding HTML
    for section in sections:
        section_type = section["type"]

        # Hero Banner Section
        if section_type == "hero_banner":
            hero_tagline = section["content"]["tagline"]
            hero_cta = section["content"]["cta"]
            hero_image_path = generate_hero_image(prompt)  # Placeholder for the hero image

            html_sections += f"""
            <div class="hero-modern">
                <div class="hero-text-content">
                    <h1>{hero_tagline}</h1>
                    <a href="#" class="cta">{hero_cta}</a>
                </div>
                <div class="hero-image-content">
                    <img src="{hero_image_path}" alt="Hero Image">
                </div>
            </div>
            """

        # Three-Point Description Section
        elif section_type == "three_point_description":
            points = section["content"]["points"]
            name = section["name"]
            points_html = ''.join([
                f"<div class='feature'><div class='feature-number'>{i+1}</div><h3>{point['title']}</h3><p>{point['description']}</p></div>"
                for i, point in enumerate(points)
            ])
            html_sections += f"""
            <div class="features-section">
                <h2>{name}</h2>
                <div class="features">
                    {points_html}
                </div>
            </div>
            """

        # Text and Image Split Section
        elif section_type == "text_image_section":
            text = section["content"]["text"]
            cta_text = section["content"]["cta"]
            image_url = generate_hero_image(prompt, text)  # Placeholder for the feature image

            if image_section == 1:
                # Text on the left, image on the right
                html_sections += f"""
                <section class="split-section">
                    <div class="split-container">
                        <div class="split-text">
                            <p>{text}</p>
                            <a href="#" class="cta-split">{cta_text}</a>
                        </div>
                        <div class="split-image">
                            <img src="{image_url}" alt="Feature Image" />
                        </div>
                    </div>
                </section>
                """
                image_section = 0  # Toggle to show image on the left next
            else:
                # Image on the left, text on the right
                html_sections += f"""
                <section class="split-section">
                    <div class="split-container">
                        <div class="split-image">
                            <img src="{image_url}" alt="Feature Image" />
                        </div>
                        <div class="split-text">
                            <p>{text}</p>
                            <a href="#" class="cta-split">{cta_text}</a>
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
        <title>Modern Haven Landing Page</title>
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f7f7f7;
                color: #333;
            }}
            nav {{
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            nav a {{
                color: #333;
                margin-right: 25px;
                font-size: 18px;
                font-weight: bold;
                text-decoration: none;
            }}
            nav a:hover {{
                color: #ff5a5a;
            }}

            /* Hero Section */
            .hero-modern {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 100px 20px;
                background: linear-gradient(to right, #f9f9f9, #fafafa);
            }}
            .hero-modern .hero-text-content {{
                flex: 1;
                max-width: 600px;
            }}
            .hero-modern h1 {{
                font-size: 56px;
                line-height: 1.2;
                color: #2d2d2d;
                margin-bottom: 20px;
            }}
            .hero-modern .cta {{
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 50px;
                text-transform: uppercase;
                transition: background-color 0.3s ease;
            }}
            .hero-modern .cta:hover {{
                background-color: #ff5a5a;
            }}
            .hero-modern .hero-image-content {{
                flex: 1;
                text-align: center;
            }}
            .hero-modern .hero-image-content img {{
                max-width: 80%;
                border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
            }}

            /* Features Section */
            .features-section {{
                padding: 60px 20px;
                background-color: #ffffff;
            }}
            .features-section h2 {{
                font-size: 40px;
                color: #2d2d2d;
                margin-bottom: 30px;
                text-align: center;
            }}
            .features {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                max-width: 1200px;
                margin: 0 auto;
                gap: 40px;
            }}
            .feature {{
                padding: 30px;
                border-radius: 15px;
                width: 100%;
                text-align: left;
                transition: transform 0.3s ease;
            }}
            .feature:hover {{
                transform: translateY(-10px);
            }}
            .feature-number {{
                display: inline-block;
                background-color: #2d2d2d;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 50%;
                margin-bottom: 15px;
            }}
            .feature h3 {{
                font-size: 24px;
                margin-bottom: 10px;
                color: #ff5a5a;
            }}

            /* Split Section */
            .split-section {{
                padding: 60px 20px;
                background-color: #fafafa;
            }}
            .split-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .split-text {{
                flex: 1;
                padding-right: 20px;
                margin-left: 20px;
            }}
            .split-text p {{
                font-size: 18px;
                color: #2d2d2d;
            }}
            .cta-split {{
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 25px;
                border-radius: 20px;
                text-transform: uppercase;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }}
            .cta-split:hover {{
                background-color: #ff5a5a;
            }}
            .split-image {{
                flex: 1;
                text-align: right;
            }}
            .split-image img {{
                max-width: 100%;
                border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
            }}

            /* Footer */
            .footer {{
                background-color: #2d2d2d;
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