import os
import fitz  # PyMuPDF
import pandas as pd
from bs4 import BeautifulSoup
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Path to the rules file
rules_file_path = 'rules.txt'

def load_rules():
    """Load rules from the text file if it exists and is not empty, otherwise return None."""
    if os.path.exists(rules_file_path):
        with open(rules_file_path, 'r') as file:
            rules = file.read()
        if rules:
            return rules
    return None

def save_rules(rules):
    """Save rules to the text file."""
    with open(rules_file_path, 'w') as file:
        file.write(rules)

def textFromAI(prompt):
    """Generate text from AI based on prompt and input text."""
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": ""}
        ]
    )
    story = res.choices[0].message.content
    return str(story)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def generate_rules_from_document(document_path):
    """Generate rules from a document using an LLM call."""
    document_text = extract_text_from_pdf(document_path)
    prompt = ("Generate a list of rules for an LLM to follow when reading further documents. "
              "The LLM will utilize these rules to analyze input data and see if items need to be "
              "included in a report (that the rules are based on) or flagged for review by a human.\n")
    generated_rules = textFromAI(prompt)
    save_rules(generated_rules)
    return generated_rules

def display_rules(rules):
    """Display the current rules."""
    print("Current Rules:\n")
    print(rules)

def edit_rules(rules):
    """Edit the existing rules."""
    while True:
        display_rules(rules)
        choice = input("Do you want to edit the rules? (yes/no): ")
        if choice.lower() == 'yes':
            new_rules = input("Enter the new rules: ")
            save_rules(new_rules)
            rules = new_rules
        else:
            break

def extract_text_from_html(html_path):
    """Extract text from an HTML file."""
    with open(html_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()
    return text

def extract_text_from_spreadsheet(spreadsheet_path):
    """Extract text from a spreadsheet (CSV or Excel)."""
    if spreadsheet_path.endswith('.csv'):
        df = pd.read_csv(spreadsheet_path)
    else:
        df = pd.read_excel(spreadsheet_path)
    text = df.to_string(index=False)
    return text

def analyze_document_with_rules(document_text, rules):
    """Analyze the document using the generated rules and return the form submission data."""
    prompt = "Analyze the following document based on the given rules:\n\n"
    prompt += f"Rules:\n{rules}\n\nDocument:\n"
    prompt += ("VERY IMPORTANT!!!! Please return the result in a csv file with the format of: "
               "idx, info about the purchase, amount, confidence interval that this item satisfies given rules (0-100%), date")
    prompt += "Please make sure to be robust in this, include all items that could possibly be included, but make sure to attach a confidence interval to let a human know if it needs to be reviewed."
    form_submission_data = textFromAI(prompt + "\n" + document_text)
    return form_submission_data

def run_rules_on_document(document_path, file_type):
    """Run the generated rules on a new document and output the form submission info."""
    if file_type == 'pdf':
        document_text = extract_text_from_pdf(document_path)
    elif file_type == 'html':
        document_text = extract_text_from_html(document_path)
    elif file_type in ['csv', 'xls', 'xlsx']:
        document_text = extract_text_from_spreadsheet(document_path)
    else:
        print("Unsupported file type.")
        return
    
    rules = load_rules()
    if rules is None:
        print("No rules found. Please generate rules first.")
        return
    
    form_submission_data = analyze_document_with_rules(document_text, rules)

    # Split the response into lines and process it into a DataFrame
    lines = form_submission_data.strip().split('\n')
    header = lines[0].split(', ')
    rows = [line.split(', ') for line in lines[1:] if line.strip()]

    # Create DataFrame
    df = pd.DataFrame(rows, columns=header)
    
    output_csv_path = 'form_submission_data.csv'
    df.to_csv(output_csv_path, index=False)
    
    print("Form Submission Data:")
    print(df)
    
    print(f"Submission data saved to {output_csv_path}")

def select_document():
    """Display a list of documents in the './docs/' directory and allow the user to select one."""
    docs_dir = './docs/'
    files = os.listdir(docs_dir)
    files = [f for f in files if os.path.isfile(os.path.join(docs_dir, f))]

    if not files:
        print("No documents found in the './docs/' directory.")
        return None

    print("Select a document to process:")
    for idx, file in enumerate(files):
        print(f"{idx + 1}. {file}")

    choice = int(input("Enter the number of the document you want to select: "))
    if 1 <= choice <= len(files):
        return os.path.join(docs_dir, files[choice - 1])
    else:
        print("Invalid choice.")
        return None

def main():
    rules = load_rules()
    if rules is None:
        rules = generate_rules_from_document("./docs/regs1.pdf")
        print("Rules have been generated and saved.")
    else:
        while True:
            choice = input("Do you want to (v)iew/edit rules, (r)un the rules on a new document, or (q)uit? (v/r/q): ")
            if choice.lower() == 'v':
                edit_rules(rules)
            elif choice.lower() == 'r':
                document_path = select_document()
                if document_path:
                    file_type = document_path.split('.')[-1].lower()
                    run_rules_on_document(document_path, file_type)
            elif choice.lower() == 'q':
                break
            else:
                print("Invalid choice, please enter 'v' to view/edit rules, 'r' to run the rules on a new document, or 'q' to quit.")

if __name__ == "__main__":
    main()
