from flask import Flask, render_template, redirect, url_for, request, flash, session
from dotenv import load_dotenv
load_dotenv()
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import traceback


app = Flask(__name__)
# Use an environment-provided secret key in production
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Needed for session management

# CRITICAL: Disable session cookie expiration to prevent state mismatch errors
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# --- Basic error logging (write to console only, not a file) ---
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Google OAuth (Authlib) setup
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=app.config.get('GOOGLE_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


@app.errorhandler(500)
def handle_500(e):
    # Log full traceback to error.log for debugging
    tb = traceback.format_exc()
    logging.error('Internal Server Error:\n%s', tb)
    # Return a minimal 500 response (template removed)
    return ("<h1>Internal Server Error</h1>"
            "<p>Something went wrong on the server. The error has been logged.</p>"), 500


# --- Google OAuth routes ---
@app.route('/login/google')
def login_google():
    # Redirect user to Google's OAuth 2.0 authorization page
    # Allow forcing the redirect URI via env var so it exactly matches
    # what's registered in Google Cloud Console (e.g. use 127.0.0.1 vs localhost).
    session.permanent = True  # Make session persist across restarts
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI') or url_for('auth_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/auth/google')
def auth_google():
    # Google will redirect back to this route after authorization
    try:
        token = oauth.google.authorize_access_token()
        # Retrieve user info from Google's UserInfo endpoint
        resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
        userinfo = resp.json()
        email = userinfo.get('email')
        name = userinfo.get('name') or userinfo.get('given_name')
        picture = userinfo.get('picture')

        if not email:
            flash('Could not retrieve email from Google account.', 'danger')
            return redirect(url_for('login'))

        global USERS
        USERS = load_users()
        # Create a new user entry if not present. Password is None for OAuth users.
        if email not in USERS:
            USERS[email] = {'password': None, 'name': name, 'oauth': 'google', 'picture': picture}
            save_users(USERS)
        else:
            # Update picture for existing Google OAuth users
            if USERS[email].get('oauth') == 'google':
                USERS[email]['picture'] = picture
                save_users(USERS)

        login_user(User(email))
        return redirect(url_for('home'))

    except Exception as e:
        logging.error('Google OAuth error: %s', e)
        flash('Google sign-in failed. Try again or use username/password.', 'danger')
        return redirect(url_for('login'))

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
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_jobs = []
    
    try:
        for city, url in LOCATIONS.items():
            print(f"Checking {city}...")
            
            try:
                driver.get(url)
                time.sleep(3)
                
                page_html = driver.page_source
                soup = BeautifulSoup(page_html, "html.parser")
                
                job_links = soup.find_all("a", href=lambda href: href and "/Home/JobPosting/" in href)
                
                seen_urls = set()
                count_for_city = 0
                
                for link in job_links:
                    href = link['href']
                    full_link = f"https://www.edjoin.org{href}"
                    title = link.get_text(strip=True)
                    
                    try:
                        job_id = int(href.split("/")[-1])
                    except:
                        job_id = 0
                    
                    if not title or full_link in seen_urls:
                        continue

                    card = link.find_parent(lambda tag: tag.name == 'div' and tag.find(class_='salary-p'))
                    
                    salary = "Salary not listed"
                    deadline = "Open until filled"
                    district = "District info not found"

                    if card:
                        salary_tag = card.find(class_="salary-p")
                        if salary_tag:
                            salary = salary_tag.get_text(strip=True)

                        deadline_span = card.find("span", class_="deadline")
                        if deadline_span:
                            deadline_text = deadline_span.parent.get_text(strip=True)
                            deadline = deadline_text.replace("Deadline:", "").strip()

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

    print("Sorting by Job ID (Newest First) regardless of location...")
    all_jobs.sort(key=lambda x: -x['id'])

    return all_jobs

def get_initials(name):
    """Extract initials from a name string"""
    if not name:
        return 'U'
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

@app.route('/')
@login_required
def home():
    job_list = get_jobs_with_browser()
    user_data = None
    user_initials = 'U'
    
    # Get current user data
    if current_user.is_authenticated:
        user_data = USERS.get(current_user.id, {})
        if user_data and user_data.get('name'):
            user_initials = get_initials(user_data.get('name'))
    
    return render_template('index.html', jobs=job_list, count=len(job_list), user_data=user_data, current_user=current_user, user_initials=user_initials)


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
    app.run(debug=True, port=5000, use_reloader=False)