# ⭐ Edu Job Scraper Bot

A Flask + Selenium automation tool that scrapes the latest IT job postings from EdJoin across multiple Southern California counties.

It launches a headless Chrome browser, parses listings with BeautifulSoup, and displays all results in a clean, prioritized UI.

## 🚀 Features

### 🌎 Scrapes job postings from:
* 🟥 **Los Angeles County**
* 🟧 **Orange County**
* 🟩 **Riverside County**
* 🟦 **San Bernardino County** 



### 🔍 Extracts job details:
* 🧑‍💼 **Job Title**
* 🏫 **District Name**
* 💵 **Salary** 
* 📅 **Deadline**
* 🔗 **Direct Posting URL**

### 📊 Smart Sorting & UI:
* ⬇️ **Priority Sorting:** List is default sorted by **Newest Posting** first.
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
py -m pip install -r requirements.txt
```
### 2.1 Google Sign-In (optional)
To enable signing in with Google you need to create OAuth 2.0 credentials in Google Cloud Console:

1. Go to https://console.cloud.google.com/apis/credentials and create an OAuth Client ID (Application type: Web application).
2. Add an Authorized redirect URI: `http://localhost:5000/auth/google`
	 - Note: Google requires an exact match for redirect URIs. If you access the site via `http://127.0.0.1:5000` you must also register `http://127.0.0.1:5000/auth/google` in the Google Console. You can either:
		 - Register both `http://localhost:5000/auth/google` and `http://127.0.0.1:5000/auth/google`, or
		 - Set an explicit redirect URI in your environment and register that exact URI (example below).
3. Copy the `Client ID` and `Client secret`.
4. Set the following environment variables in your shell or in a `.env` file at the project root:

```powershell
$env:GOOGLE_CLIENT_ID = 'your-client-id'
$env:GOOGLE_CLIENT_SECRET = 'your-client-secret'
$env:FLASK_SECRET_KEY = 'a-secure-random-secret'
```

If you prefer a `.env` file, create a file named `.env` with these entries:

```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
FLASK_SECRET_KEY=a-secure-random-secret
```

If you need the redirect to always match a specific host, add `OAUTH_REDIRECT_URI` to the `.env` (and register that exact URI in Google Cloud Console). Example:

```
OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/google
```

When Google OAuth is configured and the environment variables are present, the login page will show a "Continue with Google" button.
### 3. Run the App
* Start the scraper by running the Python script:
```powershell
py app.py
```
### 4. View Results
Once the script says ```Running on http://127.0.0.1:5000```, open your web browser and go to:

👉 http://127.0.0.1:5000

(Note: The first load may take 10-15 seconds as the scraper visits all 4 URLs in the background).
