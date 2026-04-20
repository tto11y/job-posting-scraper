import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from bs4 import BeautifulSoup

URLs = [
    "https://www.stepstone.de/stellenangebote--Spezialist-in-Application-Development-Fullstack-Koeln-HDI-AG--13855176-inline.html?rltr=103_3_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Cloud-Solution-Architekt-w-m-d-Frankfurt-am-Main-DekaBank-Deutsche-Girozentrale--13851248-inline.html?rltr=106_6_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Expert-DevSecOps-DXL-m-w-d-Duesseldorf-Unterfoehring-Vodafone-GmbH--13914161-inline.html?rltr=112_12_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Backend-Entwickler-m-w-d-Osnabrueck-Hamburg-Hellmann-Worldwide-Logistics-SE-Co-KG--13820969-inline.html?rltr=121_21_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Developer-w-m-d-Backend-Koeln-Cologne-Intelligence--13678170-inline.html?rltr=125_125_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--DevOps-Engineer-all-genders-Berlin-gematik-GmbH--13764167-inline.html?rltr=3_3_25_crl_m_0_0_0_0_0_0&cs=true",
    "https://www.stepstone.de/stellenangebote--Software-Engineer-fuer-Datenprojekte-Karlsruhe-Koeln-Muenchen-Hamburg-Stuttgart-Berlin-Erlangen-inovex-GmbH--10481680-inline.html?rltr=141_16_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Fullstack-eBanking-Entwickler-Developer-w-m-d-bundesweit-z-B-Hamburg-Berlin-Koeln-Bonn-Frankfurt-am-Main-Stuttgart-Muenchen-SYNGENIO-AG--13806180-inline.html?rltr=142_17_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Engineer-Cloud-AI-Integration-m-w-d-Muenchen-TekkMinds-AG--13748644-inline.html?rltr=151_1_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Developer-m-w-d-Alzenau-Boppard-Buchholz-Dortmund-Hamburg-Ehrhardt-Partner-Group--12760367-inline.html?rltr=158_8_25_seorl_m_1_0_0_0_0_0",
    # ... add all URLs here
]

async def scrape_vacancy(browser_context, url):
    page = await browser_context.new_page()

    print(f"Scraping: {url}")

    try:
        # Navigate and wait for the main content to load
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Optional: Wait a bit to simulate human reading
        await asyncio.sleep(2)

        # Extract the JSON-LD structured data (The "Golden Source")
        scripts = await page.locator('script[type="application/ld+json"]').all()
        job_data = {}

        for script in scripts:
            content = await script.inner_text()
            data = json.loads(content)
            # Looking for the 'JobPosting' schema
            if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                job_data = data
                break

        print(f"job_data: {job_data}")

        # Parse the specifics
        role_name = job_data.get("title", "N/A")
        company_name = job_data.get("hiringOrganization", {}).get("name", "N/A")

        # Extract Skills (Skills are usually buried in the description)
        description_html = job_data.get("description", "")
        soup = BeautifulSoup(description_html, "html.parser")
        description_text = soup.get_text(separator=" ")

        tech_keywords = ["Go", "Golang", "Java", "Spring Boot", "Angular", "React", "TypeScript", "Python", "SQL", "Docker", "Kubernetes"]
        found_skills = [skill for skill in tech_keywords if skill.lower() in description_text.lower()]

        return {
            "Company": company_name,
            "Role": role_name,
            "Skills": ", ".join(found_skills),
            "Link / Job Posting": url
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"Company": "ERROR", "Role": "ERROR", "Skills": str(e), "URL": url}
    finally:
        await page.close()

async def main():

    stealth = Stealth(
        init_scripts_only=True
    )

    async with async_playwright() as p:
        # Launch browser - headless=False helps if you need to solve a manual captcha
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        # applying stealth to context
        await stealth.apply_stealth_async(context)

        results = []
        for url in URLs:
            data = await scrape_vacancy(context, url)
            results.append(data)
            await asyncio.sleep(3)

        # Export to CSV
        df = pd.DataFrame(results)
        df.to_csv("stepstone_leads.csv", index=False, encoding="utf-8-sig")
        print("\nSuccess! Exported to stepstone_leads.csv")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())