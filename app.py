from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def scrape_linkedin_jobs(keyword):
    """Scrapes LinkedIn jobs posted in the last 24 hours based on the keyword."""
    linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&f_TPR=r86400"  # 24-hour filter

    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open LinkedIn jobs page
    driver.get(linkedin_url)
    time.sleep(3)  # Allow time for page to load

    # Extract job details using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    jobs = []
    job_cards = soup.find_all("div", class_="base-card")

    for job in job_cards[:10]:  # Limit to first 10 jobs
        title_elem = job.find("h3", class_="base-search-card__title")
        company_elem = job.find("h4", class_="base-search-card__subtitle")
        location_elem = job.find("span", class_="job-search-card__location")
        link_elem = job.find("a", class_="base-card__full-link")

        title = title_elem.text.strip() if title_elem else "No Title"
        company = company_elem.text.strip() if company_elem else "No Company"
        location = location_elem.text.strip() if location_elem else "No Location"
        link = link_elem["href"] if link_elem else "#"

        jobs.append({"title": title, "company": company, "location": location, "link": link})

    return jobs


@app.route("/", methods=["GET", "POST"])
def home():
    """Handles the search request and renders job results."""
    jobs = []
    if request.method == "POST":
        keyword = request.form["keyword"]
        if keyword:
            jobs = scrape_linkedin_jobs(keyword)

    return render_template("index.html", jobs=jobs)


if __name__ == "__main__":
    app.run(debug=True)
