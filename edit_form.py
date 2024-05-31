from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Define the form data
form_data = {
    "pdfjs_internal_id_877R": "John Doe",
    # Add other fields as necessary
}

# Set up the WebDriver without headless mode
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the PDF form webpage
pdf_form_url = "https://www.fppc.ca.gov/content/dam/fppc/NS-Documents/TAD/Lobbying/Lobbyist-Form-Folder/635_7.1.16.pdf"
driver.get(pdf_form_url)

# Wait for the page to load completely
driver.implicitly_wait(5)  # seconds

# Execute JavaScript to fill in the form fields
for field_id, value in form_data.items():
    try:
        # Use JavaScript to set the value of the input field
        script = f'document.getElementById("{field_id}").value = "{value}";'
        driver.execute_script(script)
    except Exception as e:
        print(f"Could not find or fill field {field_id}: {e}")

# If there is a submit button and you want to submit the form, you can do so
# For example, if there is a submit button with a specific name or ID
# submit_button = driver.find_element(By.NAME, "submit")
# submit_button.click()

# Optionally, you can save the filled PDF or take further actions

# Close the WebDriver
# Note: Commenting out quit so you can see the browser
# driver.quit()
