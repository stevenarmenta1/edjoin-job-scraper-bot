from flask import Flask, render_template
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

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
def home():
    job_list = get_jobs_with_browser()
    return render_template('index.html', jobs=job_list, count=len(job_list))

if __name__ == '__main__':
    app.run(debug=True, port=5000)