import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Step 1: Extract text from PDF using fitz


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Step 2: Draw text onto an image using a custom font


def draw_text_to_image(text, font_path, image_size_pixels, font_size):
    # Create a blank white image
    image = Image.new('RGB', image_size_pixels, 'white')
    draw = ImageDraw.Draw(image)

    # Load the custom font
    font = ImageFont.truetype(font_path, font_size)

    # Draw the text onto the image
    draw.text((10, 10), text, font=font, fill='black')

    return np.array(image)

# Step 3: Convert the image to black and white using cv2


def convert_to_black_and_white(image_array):
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    _, bw_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    return bw_image

# Step 4: Save the final image as PNG with the specified DPI


def save_image(image_array, output_path, dpi):
    # Convert the NumPy array to a PIL image
    pil_image = Image.fromarray(image_array)
    pil_image.save(output_path, dpi=(dpi, dpi))


# Paths to the PDF, font, and output image

# Step 1: Extract text from PDF using fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Step 2: Draw text onto an image using a custom font


def draw_text_to_image(text, font_path, image_size_pixels, font_size):
    # Create a blank white image
    image = Image.new('RGB', image_size_pixels, 'white')
    draw = ImageDraw.Draw(image)

    # Load the custom font
    font = ImageFont.truetype(font_path, font_size)

    # Draw the text onto the image
    draw.text((10, 10), text, font=font, fill='black')

    return np.array(image)

# Step 3: Convert the image to black and white using cv2


def convert_to_black_and_white(image_array):
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    _, bw_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    return bw_image

# Step 4: Save the final image as PNG with the specified DPI


def save_image(image_array, output_path, dpi):
    # Convert the NumPy array to a PIL image
    pil_image = Image.fromarray(image_array)
    pil_image.save(output_path, dpi=(dpi, dpi))


# Paths to the PDF, font, and output image
pdf_path = 'sample.pdf'
font_path = 'tahoma.ttf'
output_path = 'output_image.png'
# DPI and size in inches
dpi = 152
image_size_inches = (8.0, 12.0)  # Width, Height in inches

# Calculate image size in pixels
image_size_pixels = (
    int(image_size_inches[0] * dpi), int(image_size_inches[1] * dpi))

# Extract text from the PDF
text = extract_text_from_pdf(pdf_path)

# Draw the extracted text onto an image
font_size = 20
image_with_text = draw_text_to_image(
    text, font_path, image_size_pixels, font_size)

# Convert the image to black and white
bw_image = convert_to_black_and_white(image_with_text)

# Save the final black and white image as PNG with the specified DPI
save_image(bw_image, output_path, dpi)

print(f"The image has been saved as {output_path} with a DPI of {dpi}")


# DPI and size in inches
dpi = 152
image_size_inches = (8.0, 12.0)  # Width, Height in inches

# Calculate image size in pixels
image_size_pixels = (
    int(image_size_inches[0] * dpi), int(image_size_inches[1] * dpi))

# Extract text from the PDF
text = extract_text_from_pdf(pdf_path)

# Draw the extracted text onto an image
font_size = 20
image_with_text = draw_text_to_image(
    text, font_path, image_size_pixels, font_size)

# Convert the image to black and white
bw_image = convert_to_black_and_white(image_with_text)

# Save the final black and white image as PNG with the specified DPI
save_image(bw_image, output_path, dpi)

print(f"The image has been saved as {output_path} with a DPI of {dpi}")
