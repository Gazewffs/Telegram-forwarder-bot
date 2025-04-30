import io
import os
import re
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from config import IMAGE_PROCESSING, IMAGE_REPLACEMENT
import logging

logger = logging.getLogger(__name__)

def should_replace_image(caption=None):
    """
    Determine if an image should be replaced based on configuration and caption.
    
    Args:
        caption: The image caption or None
        
    Returns:
        Boolean indicating if the image should be replaced
    """
    # If image replacement is not enabled, never replace
    if not IMAGE_REPLACEMENT.get("enabled", False):
        return False
    
    # If the replace_only_with_caption setting is enabled and there's no caption, don't replace
    if IMAGE_REPLACEMENT.get("replace_only_with_caption", False) and not caption:
        return False
    
    # If replacing all images is enabled, and we passed the caption check, replace
    if IMAGE_REPLACEMENT.get("replace_all_images", False):
        return True
    
    # If no caption at this point, don't replace
    if not caption:
        return False
    
    # Check if any patterns match the caption
    for pattern in IMAGE_REPLACEMENT.get("patterns_to_match", []):
        if re.search(pattern, caption):
            return True
    
    return False

def get_replacement_image():
    """
    Get the replacement image as a BytesIO object.
    
    Returns:
        BytesIO object containing the replacement image
    """
    try:
        replacement_path = IMAGE_REPLACEMENT.get("replacement_path", "assets/replacement_image.jpg")
        
        # Check if replacement image exists
        if not os.path.exists(replacement_path):
            logger.error(f"Replacement image not found at: {replacement_path}")
            # Create a simple replacement image
            img = Image.new('RGB', (800, 400), color=(100, 150, 200))
            draw = ImageDraw.Draw(img)
            draw.text((400, 200), 'Replacement Image', fill=(255, 255, 255), 
                      anchor='mm' if hasattr(draw, 'textbbox') else None)
        else:
            # Load the replacement image
            img = Image.open(replacement_path)
        
        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error getting replacement image: {e}")
        # Create a simple fallback image
        img = Image.new('RGB', (400, 200), color=(255, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer

async def process_image(photo_file, caption=None):
    """
    Process an image with the configured modifications or replace it.
    
    Args:
        photo_file: Telegram File object for the photo
        caption: The caption of the image (optional)
        
    Returns:
        BytesIO object containing the processed or replacement image
    """
    # Check if we should replace the image
    if should_replace_image(caption):
        logger.info("Replacing image with configured replacement image")
        return get_replacement_image()
    
    # Otherwise, process the original image
    try:
        # Download the photo to a bytes buffer
        photo_data = await photo_file.download_as_bytearray()
        buffer = io.BytesIO(photo_data)
        
        # Open the image with PIL
        img = Image.open(buffer)
        
        # Apply modifications based on config
        img = apply_image_modifications(img)
        
        # Save the modified image to a new buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG')
        output_buffer.seek(0)
        
        return output_buffer
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        # Return the original image in case of error
        if 'buffer' in locals():
            buffer.seek(0)
            return buffer
        else:
            return None

def apply_image_modifications(img):
    """
    Apply configured modifications to an image.
    
    Args:
        img: PIL Image object
        
    Returns:
        Modified PIL Image object
    """
    # Resize image if enabled
    resize_config = IMAGE_PROCESSING["resize"]
    if resize_config["enabled"]:
        img = resize_image(
            img, 
            resize_config["max_width"], 
            resize_config["max_height"],
            resize_config["keep_aspect_ratio"]
        )
    
    # Apply enhancements if enabled
    enhancements_config = IMAGE_PROCESSING["enhancements"]
    if enhancements_config["enabled"]:
        img = apply_enhancements(img, {
            "brightness": enhancements_config["brightness"],
            "contrast": enhancements_config["contrast"],
            "sharpness": enhancements_config["sharpness"]
        })
    
    # Add watermark if enabled
    watermark_config = IMAGE_PROCESSING["watermark"]
    if watermark_config["enabled"]:
        img = add_watermark(
            img,
            watermark_config["text"],
            watermark_config["position"],
            watermark_config["font_size"],
            watermark_config["font_color"]
        )
    
    return img

def resize_image(img, max_width, max_height, keep_aspect=True):
    """
    Resize an image while optionally maintaining aspect ratio.
    
    Args:
        img: PIL Image object
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        keep_aspect: Whether to maintain aspect ratio
        
    Returns:
        Resized PIL Image object
    """
    original_width, original_height = img.size
    
    # If image is already smaller, no need to resize
    if original_width <= max_width and original_height <= max_height:
        return img
    
    if keep_aspect:
        # Calculate ratio to maintain aspect ratio
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
    else:
        new_width = max_width
        new_height = max_height
    
    return img.resize((new_width, new_height), Image.LANCZOS)

def apply_enhancements(img, filters):
    """
    Apply image enhancements like brightness, contrast, and sharpness.
    
    Args:
        img: PIL Image object
        filters: Dictionary of filter settings
        
    Returns:
        Enhanced PIL Image object
    """
    if "brightness" in filters:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(filters["brightness"])
    
    if "contrast" in filters:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(filters["contrast"])
    
    if "sharpness" in filters:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(filters["sharpness"])
    
    return img

def add_watermark(
    img, 
    text, 
    position="bottom-right", 
    font_size=20, 
    font_color=(255, 255, 255, 128)
):
    """
    Add a text watermark to an image.
    
    Args:
        img: PIL Image object
        text: Watermark text
        position: Position of watermark (top-left, top-right, bottom-left, bottom-right, center)
        font_size: Font size for the watermark
        font_color: RGBA color tuple for the watermark
        
    Returns:
        PIL Image with watermark
    """
    # Create a copy of the image with alpha channel
    img_with_watermark = img.copy()
    if img_with_watermark.mode != 'RGBA':
        img_with_watermark = img_with_watermark.convert('RGBA')
    
    # Create a transparent overlay for the watermark
    overlay = Image.new('RGBA', img_with_watermark.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to use a standard font, fallback to default if not available
    try:
        # Try to find a font on the system
        font_path = None
        common_fonts = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Common on Linux
            '/System/Library/Fonts/Helvetica.ttc',  # macOS
            'C:\\Windows\\Fonts\\arial.ttf'  # Windows
        ]
        
        for path in common_fonts:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Fallback to default font
            font = ImageFont.load_default()
    except Exception:
        # If all else fails, use default font
        font = ImageFont.load_default()
    
    # Calculate text size
    try:
        # Different methods based on Pillow version
        if hasattr(draw, 'textbbox'):
            # Newer Pillow versions
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            text_height = bottom - top
        elif hasattr(draw, 'textsize'):
            # Medium Pillow versions
            text_width, text_height = draw.textsize(text, font=font)
        elif hasattr(font, 'getsize'):
            # Older Pillow versions
            text_width, text_height = font.getsize(text)
        else:
            # Fallback for very old versions
            text_width, text_height = 100, 20  # Use a reasonable default size
    except Exception as e:
        logger.error(f"Error calculating text size: {e}")
        text_width, text_height = 100, 20  # Use a reasonable default size
    
    # Determine position
    width, height = img_with_watermark.size
    padding = 10  # Padding from edges
    
    if position == "top-left":
        x, y = padding, padding
    elif position == "top-right":
        x, y = width - text_width - padding, padding
    elif position == "bottom-left":
        x, y = padding, height - text_height - padding
    elif position == "bottom-right":
        x, y = width - text_width - padding, height - text_height - padding
    elif position == "center":
        x, y = (width - text_width) // 2, (height - text_height) // 2
    else:
        # Default to bottom-right
        x, y = width - text_width - padding, height - text_height - padding
    
    # Draw watermark text
    try:
        # Use textbbox for newer Pillow versions
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((x, y), text, font=font)
            draw.text((x, y), text, font=font, fill=font_color)
        else:
            # Fallback for older Pillow versions
            draw.text((x, y), text, font=font, fill=font_color)
    except Exception as e:
        logger.error(f"Error adding watermark text: {e}")
        # Fallback to simpler text rendering
        draw.text((x, y), text, fill=font_color)
    
    # Composite the overlay onto the original image
    img_with_watermark = Image.alpha_composite(img_with_watermark, overlay)
    
    # Convert back to RGB if the original wasn't RGBA
    if img.mode != 'RGBA':
        img_with_watermark = img_with_watermark.convert(img.mode)
    
    return img_with_watermark