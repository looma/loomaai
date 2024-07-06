from bs4 import BeautifulSoup
import npttf2utf
from base.txthandler import TxtHandler

# Load the HTML file
with open('/Users/connorlee/Documents/loomaProgramsML/Looma24/nepali-1-2464 (dragged).html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'lxml')

# Replace text
for element in soup.find_all(string=True):
    converter = TxtHandler("./map.json")
    unconverted = open("text.txt", 'w')
    unconverted.write(element)
    converter.map_fonts("text.txt", output_file_path="out.txt", from_font="Preeti", to_font="unicode", components=[], known_unicode_fonts=[])

    converted = open("out.txt", 'r')
    element.replace_with(converted.read())

# Save the modified HTML
with open('modified_example.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))