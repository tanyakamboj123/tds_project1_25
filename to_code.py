# /// script
# requires-python = ">=3.11"
# dependencies = [
#  "pillow",
#  "pytesseract",
# ]
# ///

import os
import re
from PIL import Image
import pytesseract

# Ensure the data directory exists
os.makedirs('./data/', exist_ok=True)

# Load the image
image_path = './data/credit_card.png'
if os.path.exists(image_path):
    image = Image.open(image_path)
    # Use pytesseract to extract text from image
    text = pytesseract.image_to_string(image)
    # Search for credit card number pattern
    card_number_match = re.search(r'\b(?:\d[ -]*?){13,16}\b', text)
    if card_number_match:
        card_number = card_number_match.group(0).replace(' ', '').replace('-', '')
        # Write the credit card number to a file
        with open('./data/credit-card.txt', 'w') as output_file:
            output_file.write(card_number)
    else:
        print('No credit card number found')
else:
    print('Image not found')
