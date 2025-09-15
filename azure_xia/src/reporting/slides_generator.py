"""
HTML Presentation Generator
Converts JSON presentation outline to interactive HTML slides.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime


class SlidesGenerator:
    """Generates HTML presentation from JSON outline."""
    
    def __init__(self):
        """Initialize the slides generator."""
        self.slide_template = """
        <div class="slide" id="{slide_id}">
            <div class="slide-content">
                <h1 class="slide-title">{title}</h1>
                {content}
            </div>
            <div class="slide-footer">
                <span class="slide-number">{slide_number} / {total_slides}</span>
                <span class="navigation">
                    <button onclick="previousSlide()" {prev_disabled}>← Previous</button>
                    <button onclick="nextSlide()" {next_disabled}>Next →</button>
                </span>
            </div>
        </div>
        """
        
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation_title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow: hidden;
        }}
        
        .presentation-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .slide {{
            width: 90%;
            max-width: 1000px;
            height: 80vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            box-sizing: border-box;
            display: none;
            position: relative;
            animation: slideIn 0.5s ease-in-out;
        }}
        
        .slide.active {{
            display: block;
        }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .slide-content {{
            height: calc(100% - 60px);
            overflow-y: auto;
        }}
        
        .slide-title {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        
        .slide h2 {{
            color: #34495e;
            font-size: 1.8em;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        
        .slide h3 {{
            color: #7f8c8d;
            font-size: 1.3em;
            margin-bottom: 10px;
        }}
        
        .slide ul {{
            line-height: 1.8;
            font-size: 1.1em;
        }}
        
        .slide li {{
            margin-bottom: 10px;
            padding-left: 10px;
        }}
        
        .highlight {{
            background: #f39c12;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .metric {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
        
        .code-block {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
            overflow-x: auto;
        }}
        
        .slide-footer {{
            position: absolute;
            bottom: 20px;
            left: 40px;
            right: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 2px solid #ecf0f1;
            padding-top: 15px;
        }}
        
        .slide-number {{
            color: #7f8c8d;
            font-weight: bold;
        }}
        
        .navigation button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 14px;
        }}
        
        .navigation button:hover {{
            background: #2980b9;
        }}
        
        .navigation button:disabled {{
            background: #bdc3c7;
            cursor: not-allowed;
        }}
        
        .title-slide {{
            text-align: center;
        }}
        
        .title-slide .slide-title {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        
        .subtitle {{
            font-size: 1.5em;
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        
        .author-info {{
            font-size: 1.2em;
            color: #34495e;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        {slides_html}
    </div>
    
    <script>
        let currentSlide = 0;
        const totalSlides = {total_slides};
        
        function showSlide(n) {{
            const slides = document.querySelectorAll('.slide');
            slides.forEach(slide => slide.classList.remove('active'));
            
            if (n >= totalSlides) currentSlide = 0;
            if (n < 0) currentSlide = totalSlides - 1;
            
            slides[currentSlide].classList.add('active');
        }}
        
        function nextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                currentSlide++;
                showSlide(currentSlide);
            }}
        }}
        
        function previousSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                showSlide(currentSlide);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowLeft') previousSlide();
            if (e.key === 'Home') {{ currentSlide = 0; showSlide(currentSlide); }}
            if (e.key === 'End') {{ currentSlide = totalSlides - 1; showSlide(currentSlide); }}
        }});
        
        // Initialize
        showSlide(0);
        
        // Auto-advance for demo (uncomment if needed)
        // setInterval(nextSlide, 10000); // Advance every 10 seconds
    </script>
</body>
</html>
        """
    
    def format_list_content(self, items, list_type="bullet"):
        """Format list items as HTML."""
        if not items:
            return ""
        
        html = "<ul>"
        for item in items:
            # Highlight success indicators
            if "✅" in str(item):
                item = str(item).replace("✅", '<span class="success">✅</span>')
            
            # Highlight metrics
            if any(char.isdigit() for char in str(item)) and ("studies" in str(item).lower() or "%" in str(item)):
                html += f'<li><div class="metric">{item}</div></li>'
            else:
                html += f'<li>{item}</li>'
        
        html += "</ul>"
        return html
    
    def create_title_slide(self, slide_data: Dict, slide_num: int, total: int) -> str:
        """Create title slide."""
        content = f"""
        <div class="title-slide">
            <div class="subtitle">{slide_data.get('subtitle', '')}</div>
            <div class="author-info">
                <div><strong>{slide_data.get('student', '')}</strong></div>
                <div>{slide_data.get('date', '')}</div>
                <div>{slide_data.get('course', '')}</div>
            </div>
        </div>
        """
        
        return self.slide_template.format(
            slide_id=f"slide-{slide_num}",
            title=slide_data.get('title', ''),
            content=content,
            slide_number=slide_num,
            total_slides=total,
            prev_disabled='disabled' if slide_num == 1 else '',
            next_disabled='disabled' if slide_num == total else ''
        )
    
    def create_content_slide(self, slide_data: Dict, slide_num: int, total: int) -> str:
        """Create content slide."""
        content = ""
        
        # Handle different content types
        if 'points' in slide_data:
            content += self.format_list_content(slide_data['points'])
        
        if 'pipeline' in slide_data:
            content += "<h2>Pipeline Steps:</h2>"
            content += self.format_list_content(slide_data['pipeline'])
        
        if 'metrics' in slide_data:
            content += "<h2>Key Metrics:</h2>"
            content += self.format_list_content(slide_data['metrics'])
        
        if 'findings' in slide_data:
            content += "<h2>Research Insights:</h2>"
            content += self.format_list_content(slide_data['findings'])
        
        if 'architecture' in slide_data:
            content += "<h2>Technical Implementation:</h2>"
            content += self.format_list_content(slide_data['architecture'])
        
        if 'requirements' in slide_data:
            content += "<h2>Requirements Status:</h2>"
            content += self.format_list_content(slide_data['requirements'])
        
        if 'commands' in slide_data:
            content += "<h2>Demo Commands:</h2>"
            content += '<div class="code-block">'
            for cmd in slide_data['commands']:
                content += f"{cmd}<br>"
            content += '</div>'
            if 'note' in slide_data:
                content += f'<div class="metric">{slide_data["note"]}</div>'
        
        if 'applications' in slide_data:
            content += "<h2>Real-World Applications:</h2>"
            content += self.format_list_content(slide_data['applications'])
        
        if 'summary' in slide_data:
            content += "<h2>Summary:</h2>"
            content += self.format_list_content(slide_data['summary'])
        
        return self.slide_template.format(
            slide_id=f"slide-{slide_num}",
            title=slide_data.get('title', ''),
            content=content,
            slide_number=slide_num,
            total_slides=total,
            prev_disabled='disabled' if slide_num == 1 else '',
            next_disabled='disabled' if slide_num == total else ''
        )
    
    def generate_presentation(self, presentation_data: Dict, output_path: str):
        """Generate complete HTML presentation."""
        slides_html = ""
        slides = []
        
        # Extract slides from JSON data
        for key, slide_data in presentation_data.items():
            if key.startswith('slide_'):
                slides.append((key, slide_data))
        
        # Sort slides by number
        slides.sort(key=lambda x: int(x[0].split('_')[1]))
        
        total_slides = len(slides)
        
        # Generate each slide
        for i, (slide_key, slide_data) in enumerate(slides, 1):
            if i == 1:  # Title slide
                slide_html = self.create_title_slide(slide_data, i, total_slides)
            else:  # Content slide
                slide_html = self.create_content_slide(slide_data, i, total_slides)
            
            slides_html += slide_html
        
        # Get presentation title
        title_slide = slides[0][1] if slides else {}
        presentation_title = title_slide.get('title', 'Presentation')
        
        # Generate complete HTML
        html_content = self.html_template.format(
            presentation_title=presentation_title,
            slides_html=slides_html,
            total_slides=total_slides
        )
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path


def main():
    """Generate slides from JSON outline."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python slides_generator.py <presentation_outline.json> <output.html>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Load presentation data
    with open(json_path, 'r') as f:
        presentation_data = json.load(f)
    
    # Generate slides
    generator = SlidesGenerator()
    result_path = generator.generate_presentation(presentation_data, output_path)
    
    print(f"✅ Presentation generated: {result_path}")
    print(f"📱 Open in browser: open {result_path}")


if __name__ == "__main__":
    main()