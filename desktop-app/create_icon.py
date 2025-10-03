#!/usr/bin/env python3
"""
Simple script to create a basic icon for the CodeTantra Automation app
This creates a simple 256x256 icon with the app name
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_simple_icon():
    """Create a simple icon using PIL if available, otherwise create a placeholder"""
    if PIL_AVAILABLE:
        # Create a 256x256 image with a blue background
        img = Image.new('RGB', (256, 256), color='#2E86AB')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # Draw text
        text = "CodeTantra\nAutomation"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (256 - text_width) // 2
        y = (256 - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font, align='center')
        
        # Save as ICO
        img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("✓ Icon created successfully: icon.ico")
        return True
    else:
        print("⚠ PIL not available, creating placeholder icon file")
        # Create a simple placeholder
        with open('icon.ico', 'wb') as f:
            # Write a minimal ICO header (this won't be a valid icon but prevents errors)
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00\x68\x04\x00\x00\x16\x00\x00\x00')
        print("✓ Placeholder icon created: icon.ico")
        return True

if __name__ == "__main__":
    print("Creating icon for CodeTantra Automation...")
    if create_simple_icon():
        print("Icon creation completed!")
    else:
        print("Failed to create icon")
