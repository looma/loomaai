from bs4 import BeautifulSoup
import npttf2utf
from base.fontmapper import FontMapper

# Load the HTML file

def convert(element:str):
    mapper = FontMapper("./files/map.json")
    mappedText = mapper.map_to_unicode(element, from_font="Preeti", unescape_html_input=False, escape_html_output=False)

    return mappedText

with open('/Users/connorlee/Documents/loomaProgramsML/Looma24/nepali-1-2464 (dragged).html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'lxml')

for element in soup.find_all(string=True):
    element.replace_with(convert(element))

# Save the modified HTML
with open('./files/modified_example1.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))
