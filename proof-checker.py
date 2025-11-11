import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

file_name = input("Enter the proof file path (e.g. data/proof1.txt): ")

with open(file_name, "r") as file:
    lines = file.readlines()
    premises = lines[0].strip().split(";") if lines[0].strip() != "" else []
    conclusion = lines[1].strip()
    proof = [line.strip().split(";") if len(line.strip().split(";")) == 3 else [*line.strip().split(";"), ""] for line in lines[2:] if line.strip() != ""]

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

WebDriverWait(driver, 30).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

with open("automation-script.js", "r") as file:
    script = file.read()

driver.get("https://proofs.openlogicproject.org/")

driver.execute_script(script, premises, conclusion, proof)

results_locator = (By.CLASS_NAME, "resultsdiv")

WebDriverWait(driver, 30).until(
    lambda d: d.find_element(*results_locator).text != "Checking …"
)

result = driver.find_element(By.CLASS_NAME, "resultsdiv").text
proof = driver.find_element(By.ID, "theproof")

if result == "☺ Congratulations! This proof is correct.":
    print("\033[32mProof is correct!\033[0m")
    additional_height = 0
else:   
    print("\033[31mProof is incorrect!\033[0m")
    print("Explanation:", "\n".join(result.splitlines()[1:]), sep="\n")
    additional_height = 300

full_page_height = proof.get_property('scrollHeight')
full_page_width = proof.get_property('scrollWidth')
driver.set_window_size(full_page_width, full_page_height + additional_height)

driver.execute_script("arguments[0].scrollIntoView();", proof)

driver.get_screenshot_as_file(f"{str(datetime.datetime.now().timestamp()).split('.')[0]}.png")

driver.quit()