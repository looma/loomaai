import PyPDF2

def copy_pdf(input_pdf, output_pdf):
    with open(input_pdf, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        # Iterate through each page in the input PDF
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Write the contents to the output PDF
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

if __name__ == '__main__':
    input_pdf = '/Users/connorlee/Documents/loomaProgramsML/Looma24/pdf.pdf'
    output_pdf = './files/output.pdf'
    copy_pdf(input_pdf, output_pdf)