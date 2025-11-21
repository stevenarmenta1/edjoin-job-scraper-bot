# ⭐ Edu Job Scraper Bot

A Flask + Selenium automation tool that scrapes the latest IT job postings from EdJoin across multiple Southern California counties.

It launches a headless Chrome browser, parses listings with BeautifulSoup, and displays all results in a clean, prioritized UI.

## 🚀 Features

### 🌎 Scrapes job postings from:
* 🟦 **San Bernardino County** 
* 🟩 **Riverside County**
* 🟧 **Orange County**
* 🟥 **Los Angeles County**

### 🔍 Extracts job details:
* 🧑‍💼 **Job Title**
* 🏫 **District Name**
* 💵 **Salary** 
* 📅 **Deadline**
* 🔗 **Direct Posting URL**

### 📊 Smart Sorting & UI:
* ⬇️ **Priority Sorting:** Listings are grouped by **Newest Posting** first.
* ⚡ **Headless Selenium:** Handles dynamic JavaScript content.
* 🎨 **Visual Badges:** Color-coded indicators for locations and districts.

---

## 🛠️ Steps to run on local machine

### 1. Prerequisites
* Python installed on your machine.
* Google Chrome browser installed.

### 2. Installation
Open your PowerShell or Terminal in the project folder and install the required libraries:

```powershell
py -m pip install flask selenium beautifulsoup4 webdriver-manager
```
### 3. Run the App
* Start the scraper by running the Python script:
```powershell
py app.py
```
### 4. View Results
Once the script says ```Running on http://127.0.0.1:5000```, open your web browser and go to:

👉 http://127.0.0.1:5000

(Note: The first load may take 10-15 seconds as the scraper visits all 4 URLs in the background).
