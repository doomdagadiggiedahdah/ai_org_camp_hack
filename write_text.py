import os
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Function to create a canvas with filled form fields
def create_filled_form(data, template_path, output_path):
    c = canvas.Canvas('temp_filled_form.pdf', pagesize=letter)

    # Adjust the position based on actual coordinates of the fields
    c.drawString(150, 740, data['name'])        # Adjust coordinates as needed
    c.drawString(150, 720, data['address'])     # Adjust coordinates as needed
    c.drawString(150, 700, data['telephone'])   # Adjust coordinates as needed
    c.drawString(150, 680, data['period_covered'])  # Adjust coordinates as needed

    # Save the canvas with the filled data
    c.save()

    # Merge the form fields with the original PDF
    form = PdfReader('temp_filled_form.pdf')
    template = PdfReader(template_path)
    form_page = form.pages[0]
    template_page = template.pages[0]

    overlay = PageMerge(template_page)
    overlay.add(form_page).render()

    writer = PdfWriter(output_path)
    writer.addpage(template_page)
    # Add other pages if necessary
    for page in template.pages[1:]:
        writer.addpage(page)
    writer.write()

    # Clean up temporary file
    os.remove('temp_filled_form.pdf')

# Example data to fill in the form
data = {
    'name': 'John Doe',
    'address': '1234 Main St, Anytown, USA',
    'telephone': '555-1234',
    'period_covered': 'Q1 2024'
}

# Paths to the input and output files
template_path = './docs/635_7.1.16.pdf'
output_path = './docs/filled_form_corrected.pdf'

# Create the filled form
create_filled_form(data, template_path, output_path)
