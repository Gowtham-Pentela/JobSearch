from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

def fetch_jobs(keyword):
    """Scrape LinkedIn for job postings in the last 24 hours based on the keyword."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_TPR=r86400"  # Last 24 hours filter
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for job_card in soup.find_all("div", class_="base-card"):
        title = job_card.find("h3", class_="base-search-card__title")
        company = job_card.find("h4", class_="base-search-card__subtitle")
        location = job_card.find("span", class_="job-search-card__location")
        link = job_card.find("a", class_="base-card__full-link")

        if title and company and location and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location.text.strip(),
                "link": link["href"]
            })

    return jobs

@app.route("/", methods=["GET", "POST"])
def index():
    jobs = []
    if request.method == "POST":
        keyword = request.form.get("keyword")  # Get keyword from input box
        if keyword:
            jobs = fetch_jobs(keyword)

    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
