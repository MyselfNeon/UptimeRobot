# ---------------------------------------------------
# File Name: Image_Gen.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

from PIL import Image, ImageDraw, ImageFont
import io

def draw_dashboard(user_name, urls_data):
    # Constants for Layout
    WIDTH = 800
    HEADER_HEIGHT = 120
    ROW_HEIGHT = 80
    PADDING = 20
    
    # Calculate Total Height
    total_height = HEADER_HEIGHT + (len(urls_data) * ROW_HEIGHT) + PADDING
    
    # Create Canvas (Dark Mode)
    # Background: #1e1e2e (Dark Blue/Grey), Text: White
    img = Image.new('RGB', (WIDTH, total_height), color='#1e1e2e')
    draw = ImageDraw.Draw(img)
    
    # --- Fonts ---
    try:
        # Try loading a readable font (paths vary by OS/Docker)
        # In Docker, we might need to rely on default if no ttf is copied.
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_url = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_stats = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        # Fallback to default if font is missing
        font_header = ImageFont.load_default()
        font_url = ImageFont.load_default()
        font_stats = ImageFont.load_default()

    # --- Draw Header ---
    draw.rectangle([(0, 0), (WIDTH, HEADER_HEIGHT)], fill='#2b2b3b')
    
    draw.text((30, 30), "Uptime Monitor Dashboard", font=font_header, fill='#ffffff')
    draw.text((30, 80), f"User: {user_name}  |  Total Sites: {len(urls_data)}", font=font_stats, fill='#a6adc8')

    # --- Draw Rows ---
    y = HEADER_HEIGHT + PADDING
    
    for data in urls_data:
        url = data.get('url', 'Unknown URL')
        status_code = data.get('status', 0)
        latency = data.get('response_time', 0)
        
        # Calculate Uptime %
        total = data.get('total_checks', 1)
        up = data.get('uptime_count', 0)
        uptime_pct = round((up / total) * 100, 1) if total > 0 else 0.0
        
        # Determine Color & Status
        is_up = status_code == 200
        status_color = '#a6e3a1' if is_up else '#f38ba8' # Green or Red
        status_text = "ONLINE" if is_up else f"DOWN ({status_code})"
        
        # Draw Status Indicator (Circle)
        draw.ellipse([(30, y + 25), (60, y + 55)], fill=status_color)
        
        # Draw URL
        draw.text((80, y + 15), url, font=font_url, fill='white')
        
        # Draw Stats (Latency | Uptime)
        stats_line = f"ping: {latency}ms  |  uptime: {uptime_pct}%  |  {status_text}"
        draw.text((80, y + 45), stats_line, font=font_stats, fill='#bac2de')
        
        # Draw Divider Line
        draw.line([(30, y + ROW_HEIGHT - 5), (WIDTH - 30, y + ROW_HEIGHT - 5)], fill='#313244', width=1)
        
        y += ROW_HEIGHT

    # Save to BytesIO
    bio = io.BytesIO()
    bio.name = 'dashboard.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio
  
