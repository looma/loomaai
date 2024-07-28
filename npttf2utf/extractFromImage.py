try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
from base.fontmapper import FontMapper

# If you don't have tesseract executable in your PATH, include the following:
#pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

# Simple image to string
#text = pytesseract.image_to_string(Image.open('/Users/connorlee/Desktop/Screenshot 2024-07-27 at 11.57.15 AM.png'))
#print(text)
mapper = FontMapper("./files/map.json")
mappedText = mapper.map_to_unicode("नष्लनभच", from_font="Preeti", unescape_html_input=False, escape_html_output=False)
print("Converted: ")
print(mappedText)


"""

# Get bounding box estimates
print(pytesseract.image_to_boxes(Image.open('test.png')))

# Get verbose data including boxes, confidences, line and page numbers
print(pytesseract.image_to_data(Image.open('test.png')))

# Get information about orientation and script detection
print(pytesseract.image_to_osd(Image.open('test.png')))

"""