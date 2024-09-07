import re


def reformat_prices(text):

    pattern = r'\$(-?\d+(?:,\d{3})*(?:\.\d+)?)'
    replacement = r'\1 USD'

    reformatted_text = re.sub(pattern, replacement, text)

    return reformatted_text

# Function to read, reformat, and save the file
def process_file(file_path):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Reformat the prices in the content
    reformatted_content = reformat_prices(content)

    # Write the reformatted content back to the file or to a new file
    with open('reformatted_' + file_path, 'w') as file:
        file.write(reformatted_content)

# Specify the path to your text file
file_path = '2024.journal'

# Process the file
process_file(file_path)

print(f"Prices have been reformatted in 'reformatted_{file_path}'")
