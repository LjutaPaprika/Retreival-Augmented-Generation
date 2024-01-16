import os
from pikepdf import Pdf
from pathlib import Path

# The target PDF document to split
filename = "/Users/Vuk/Desktop/Take Home/Boeing-B737-700-800-900-Operations-Manual.pdf"

# Create a directory to save new files to
p = Path(filename)
directory = str(p.parent).replace("\\", "/")
# print(directory)

new_dir = "Documents"
path = os.path.join(directory, new_dir).replace("\\", "/")
os.mkdir(path)

# Save the exact pdf name
file = p.name
# print(file)

# Load the PDF file
pdf = Pdf.open(filename)

# Find the total number of pages
num_pages = len(pdf.pages)
# print(f"total pages :: {num_pages}")

# Define number of pages each new pdf should be (at most)
pdf_subsize = 100

# Calculate the number of new pdfs to make depending on subsize
num_files = (num_pages // pdf_subsize) + 1
# print("Number of files to create ::", num_files)

# Create each new pdf
new_pdf_files = [Pdf.new() for i in range(0, num_files)]

# the current pdf file index
new_pdf_index = 0

# Create sub pdf page ranges (eg. [[0,100], [100, 200], ...])
page_ranges = [[i*pdf_subsize, (i+1)*pdf_subsize] for i in range(0, num_files)]
# print(file2pages)

# iterate over all PDF pages
for j, page in enumerate(pdf.pages):
    # if the current iteration value (j) is within the page range of the current pdf file index
    if j in range(*page_ranges[new_pdf_index]):
        # add the j-th page to the new_pdf_index-th file
        new_pdf_files[new_pdf_index].pages.append(page)
        print(f"[*] Assigning Page {j} to the file {new_pdf_index}")
    else:
        # Declare a filename based on original file name plus the index
        name, ext = os.path.splitext(os.path.join(path, file).replace("\\", "/"))
        output_filename = f"{name}-{new_pdf_index}.pdf"
        # save the PDF file
        new_pdf_files[new_pdf_index].save(output_filename)
        print(f"[+] File: {output_filename} saved.")
        # increment the index to go to the next file
        new_pdf_index += 1
        # add the j-th page to the new_pdf_index-th file (otherwise the current, j-th page is lost)
        new_pdf_files[new_pdf_index].pages.append(page)
        print(f"[*] Assigning Page {j} to the file {new_pdf_index}")

# save the last PDF file (must be done on its own as the loop does not cover it)
name, ext = os.path.splitext(os.path.join(path, file).replace("\\", "/"))
output_filename = f"{name}-{new_pdf_index}.pdf"
new_pdf_files[new_pdf_index].save(output_filename)
print(f"[+] File: {output_filename} saved.")