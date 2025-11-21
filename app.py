from flask import Flask, render_template, redirect, url_for, request, flash, session
from dotenv import load_dotenv
load_dotenv()
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from flask_dance.contrib.google import make_google_blueprint, google


app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secret-key'  # Needed for session management

# --- Google OAuth Setup ---
# You must set these environment variables or replace with your credentials
import os
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --- Persistent User Store (JSON file) ---
USERS_FILE = 'users.json'
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {'testuser': {'password': 'testpass'}}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

USERS = load_users()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    global USERS
    USERS = load_users()
    if user_id in USERS:
        return User(user_id)
    return None

# Dictionary of locations
LOCATIONS = {
    "San Bernardino": "https://www.edjoin.org/Home/Jobs?rows=10&page=1&sort=postingDate&sortVal=0&order=DESC&keywords=null&location=san%20bernardino&searchType=&regions=&jobTypes=25&days=undefined&empType=&catID=0&onlineApps=null&recruitmentCenterID=0&stateID=undefined&regionID=null&districtID=0&searchID=0",
    "Riverside": "https://www.edjoin.org/Home/Jobs?rows=10&page=1&sort=postingDate&sortVal=0&order=DESC&keywords=null&location=riverside&searchType=&regions=&jobTypes=25&days=undefined&empType=&catID=0&onlineApps=null&recruitmentCenterID=0&stateID=undefined&regionID=null&districtID=0&searchID=0",
    "Orange": "https://www.edjoin.org/Home/Jobs?rows=10&page=1&sort=postingDate&sortVal=0&order=DESC&keywords=null&location=orange&searchType=&regions=&jobTypes=25&days=undefined&empType=&catID=0&onlineApps=null&recruitmentCenterID=0&stateID=undefined&regionID=null&districtID=0&searchID=0",
    "Los Angeles": "https://www.edjoin.org/Home/Jobs?rows=10&page=1&sort=postingDate&sortVal=0&order=DESC&keywords=null&location=los%20angeles&searchType=&regions=&jobTypes=25&days=undefined&empType=&catID=0&onlineApps=null&recruitmentCenterID=0&stateID=undefined&regionID=null&districtID=0&searchID=0"
}

def get_jobs_with_browser():
    print("Launching browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") # Added for stability
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_jobs = []
    
    try:
        for city, url in LOCATIONS.items():
            print(f"Checking {city}...")
            
            try:
                driver.get(url)
                time.sleep(3) # Wait for load
                
                page_html = driver.page_source
                soup = BeautifulSoup(page_html, "html.parser")
                
                # Find links containing /Home/JobPosting/
                job_links = soup.find_all("a", href=lambda href: href and "/Home/JobPosting/" in href)
                
                seen_urls = set()
                count_for_city = 0
                
                for link in job_links:
                    href = link['href']
                    full_link = f"https://www.edjoin.org{href}"
                    title = link.get_text(strip=True)
                    
                    # EXTRACT ID for sorting
                    try:
                        job_id = int(href.split("/")[-1])
                    except:
                        job_id = 0
                    
                    if not title or full_link in seen_urls:
                        continue

                    # --- DATA EXTRACTION ---
                    card = link.find_parent(lambda tag: tag.name == 'div' and tag.find(class_='salary-p'))
                    
                    salary = "Salary not listed"
                    deadline = "Open until filled"
                    district = "District info not found"

                    if card:
                        # 1. SALARY
                        salary_tag = card.find(class_="salary-p")
                        if salary_tag:
                            salary = salary_tag.get_text(strip=True)

                        # 2. DEADLINE
                        deadline_span = card.find("span", class_="deadline")
                        if deadline_span:
                            deadline_text = deadline_span.parent.get_text(strip=True)
                            deadline = deadline_text.replace("Deadline:", "").strip()

                        # 3. DISTRICT
                        district_tag = card.find(class_="district")
                        if district_tag:
                            district = district_tag.get_text(strip=True)
                        else:
                            all_text = list(card.stripped_strings)
                            if len(all_text) > 1 and "$" not in all_text[1] and "Deadline" not in all_text[1]:
                                district = all_text[1]

                    all_jobs.append({
                        'id': job_id,
                        'title': title,
                        'url': full_link,
                        'location': city,
                        'district': district,
                        'salary': salary,
                        'deadline': deadline
                    })
                    
                    seen_urls.add(full_link)
                    count_for_city += 1
                
                print(f"  Found {count_for_city} jobs in {city}.")
                
            except Exception as e:
                print(f"  Error checking {city}: {e}")

    finally:
        driver.quit()
        print("Browser closed.")

    # --- THE SORTING MAGIC (UPDATED TO REMOVE LOCATION SORT) ---
    
    # 1. REMOVE location_priority dictionary (not needed)
    # location_priority = {
    #     "San Bernardino": 1,
    #     "Riverside": 2,
    #     "Orange": 3,
    #     "Los Angeles": 4
    # }
    
    print("Sorting by Job ID (Newest First) regardless of location...")
    
    # 2. Sort by ONLY the Job ID (Negative sign means Descending/Newest first)
    all_jobs.sort(key=lambda x: -x['id'])

    return all_jobs

@app.route('/')

@app.route('/')
@login_required
def home():
    job_list = get_jobs_with_browser()
    return render_template('index.html', jobs=job_list, count=len(job_list))


# --- Register Route ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        global USERS
        USERS = load_users()
        if not username or not password:
            flash('Username and password required', 'danger')
        elif username in USERS:
            flash('Username already exists', 'danger')
        elif password != confirm:
            flash('Passwords do not match', 'danger')
        else:
            USERS[username] = {'password': password}
            save_users(USERS)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


# --- Google OAuth Login Route ---
@app.route('/login/google')
def login_google():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        username = user_info["email"]
        global USERS
        USERS = load_users()
        if username not in USERS:
            USERS[username] = {"password": "oauth"}
            save_users(USERS)
        login_user(User(username))
        flash(f"Logged in as {username}", "success")
        return redirect(url_for('home'))
    flash("Failed to log in with Google", "danger")
    return redirect(url_for('login'))

# --- Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        global USERS
        USERS = load_users()
        user = USERS.get(username)
        if user and user['password'] == password:
            login_user(User(username))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# --- Logout Route ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)