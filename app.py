from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def get_chrome_driver():
    """Sets up and returns a headless Chrome WebDriver for Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--no-sandbox")  # Required for Linux environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"  # Chrome binary location
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_linkedin_jobs(keyword):
    """Scrapes LinkedIn job postings for the given keyword."""
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
    
    driver = get_chrome_driver()
    driver.get(url)
    time.sleep(3)  # Allow the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    job_listings = []
    job_cards = soup.find_all("div", class_="base-search-card")

    for job in job_cards:
        try:
            company = job.find("h4", class_="base-search-card__subtitle").text.strip()
            location = job.find("span", class_="job-search-card__location").text.strip()
            apply_link = job.find("a", class_="base-card__full-link")["href"]
            job_listings.append({"Company": company, "Location": location, "Apply Link": apply_link})
        except AttributeError:
            continue

    return job_listings

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        jobs = scrape_linkedin_jobs(keyword)
        return render_template("index.html", jobs=jobs)
    return render_template("index.html", jobs=[])

@app.route("/api/jobs", methods=["GET"])
def api_jobs():
    keyword = request.args.get("keyword", "data science")  # Default search keyword
    jobs = scrape_linkedin_jobs(keyword)
    return jsonify(jobs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
