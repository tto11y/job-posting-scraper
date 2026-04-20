import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from bs4 import BeautifulSoup

URLs = [
    "https://www.stepstone.de/stellenangebote--Senior-Software-Engineer-Java-all-genders-Berlin-Hamburg-Leipzig-Bremen-Dresden-Jena-Rostock-Stralsund-Kiel-Neumuenster-adesso-SE--13797146-inline.html?rltr=53_3_25_seorl_m_1_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Java-Entwickler-m-w-d-Hannover-Frankfurt-Main-Bremen-oder-Braunschweig-Rail-Management-Consultants-International-GmbH--10048566-inline.html?rltr=58_8_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Full-Stack-Developer-Java-Angular-React-m-w-d-Deutschlandweit-Homeoffice-Avision-GmbH--9486560-inline.html?rltr=59_9_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Full-Stack-Java-Entwickler-in-all-gender-Muenchen-Nuernberg-ALTEN-GmbH--13601569-inline.html?rltr=60_10_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Full-Stack-Java-Developer-m-w-d-Ottobrunn-IABG-Industrieanlagen-Betriebsgesellschaft-mbH--13665951-inline.html?rltr=62_12_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Backend-Developer-m-w-d-Koeln-Diginet-GmbH-Co-KG-Pixum--13856060-inline.html?rltr=64_14_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Software-Developer-Cloud-Applications-und-Frontend-m-w-d-Hamburg-E-ON-Grid-Solutions-GmbH--13855555-inline.html?rltr=75_75_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--DevOps-Engineer-m-w-d-Hamburg-Bundesdruckerei-Gruppe--13855110-inline.html?rltr=77_2_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Experienced-Full-Stack-Software-Engineer-all-genders-Berlin-Hamburg-Frankfurt-am-Main-Duesseldorf-Muenchen-Stuttgart-PRODYNA-SE--13799028-inline.html?rltr=78_3_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Full-Stack-Entwickler-w-m-d-fuer-Cloud-Loesungen-Frankfurt-am-Main-DekaBank-Deutsche-Girozentrale--13859545-inline.html?rltr=86_11_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-w-m-d-Fullstack-mogena-uv-Hamburg-IT-UV-Software-GmbH--13842462-inline.html?rltr=87_12_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Fullstack-Entwickler-m-w-d-Schwerpunkt-Angular-Koeln-Toyota-Kreditbank-GmbH--13906032-inline.html?rltr=91_16_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Backend-Entwickler-w-m-d-Hamburg-HanseMerkur-Versicherungsgruppe--13827180-inline.html?rltr=92_17_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Software-Engineer-Berlin-Deutsche-Rentenversicherung-Bund--13900610-inline.html?rltr=105_5_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Engineer-m-w-d-Stuttgart-BettercallPaul-GmbH--13901660-inline.html?rltr=106_6_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Java-Softwareentwickler-API-Backend-m-w-d-Muenchen-Bayerische-Versorgungskammer--13910320-inline.html?rltr=12_12_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-in-Java-w-m-d-Muenchen-Augsburg-Ingolstadt-Aschaffenburg-Bamberg-Nuernberg-Regensburg-Wuerzburg-Pico-Engineering-GmbH--13561069-inline.html?rltr=10_10_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Backend-Developer-Java-m-w-d-Hamburg-Bundesdruckerei-Gruppe--13855461-inline.html?rltr=8_8_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Softwareentwicklerin-Hamburg-KSP-Kanzlei-Dr-Seegers-Dr-Frankenheim-Rechtsanwaltsgesellschaft-mbH--13788523-inline.html?rltr=7_7_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-IT-Consultant-Full-Stack-Java-Entwicklung-w-d-m-Muenchen-puntus-GmbH--13793589-inline.html?rltr=4_4_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Java-Backend-Softwareentwickler-w-m-d-Koeln-parcIT-GmbH--13907306-inline.html?rltr=3_3_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Developer-im-Consulting-mit-Spring-Boot-und-Cloud-Fokus-m-w-d-Frankfurt-am-Main-meiyu-GmbH--13788566-inline.html?rltr=2_2_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Full-Stack-Entwickler-m-w-d-Spring-Boot-React-Muenchen-SBK-Siemens-Betriebskrankenkasse--13914976-inline.html?rltr=1_1_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-Java-m-w-d-Muenchen-Karlsruhe-Frankfurt-am-Main-Koeln-Stuttgart-andrena-objects-ag--13401787-inline.html?rltr=13_13_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Developer-in-m-w-d-Koeln-STRABAG-BRVZ-GmbH-Co-KG--13838833-inline.html?rltr=14_14_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Java-Developer-w-m-d-Cybersecurity-Muenchen-Data-Warehouse-GmbH--13901413-inline.html?rltr=15_15_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Java-Developer-m-w-d-Berlin-Konstanz-oder-remote-Konstanz-Berlin-SEITENBAU-GmbH--13761981-inline.html?rltr=16_16_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Lead-Java-Software-Entwickler-Rechnungsmanagement-m-w-d-Hannover-Muenster-Frankfurt-am-Main-Finanz-Informatik-GmbH-Co-KG--13825373-inline.html?rltr=17_17_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Software-Engineer-Java-d-m-w-Eschborn-VR-Smart-Finanz-AG--13888526-inline.html?rltr=18_18_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Fullstack-Developer-m-w-d-Hamburg-Hannover-Stuttgart-Koeln-Berlin-Duesseldorf-Muenchen-Frankfurt-Computer-Futures--13458365-inline.html?rltr=19_19_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-Java-m-w-d-Stuttgart-DSV-IT-Service-GmbH-Ein-Unternehmen-der-DSV-Gruppe--13814544-inline.html?rltr=21_21_25_seorl_m_1_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-Java-Mensch-Muenchen-Koeln-Faktor-Zehn-GmbH--13876134-inline.html?rltr=22_22_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--DevOps-Engineer-Java-Developer-m-w-d-Input-Management-mit-SmartFix-DocAI-Hamburg-Dortmund-SIGNAL-IDUNA-Gruppe--13856630-inline.html?rltr=23_23_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Developer-m-w-d-Hamburg-EDEKA-IT-Stiftung-Co-OHG--13876634-inline.html?rltr=24_24_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Backend-Engineer-Kotlin-Java-m-w-d-Hamburg-Berlin-Visable-GmbH-Alibaba-com--13817822-inline.html?rltr=25_25_25_seorl_m_1_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Fullstack-Entwickler-w-m-d-Java-Angular-Koeln-PENSIONS-SICHERUNGS-VEREIN-VVaG-PSVaG--13868293-inline.html?rltr=26_1_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Developer-Full-Stack-Java-Angular-Produktentwicklung-all-genders-1-Paderborn-Essen-Duesseldorf-Dortmund-Koeln-adesso-insurance-solutions-GmbH--13868530-inline.html?rltr=28_3_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Softwareentwickler-Java-Backend-w-m-d-Berlin-SoftConEx-GmbH--10390189-inline.html?rltr=29_4_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Senior-Java-Entwickler-Kunden-und-Partnerkommunikation-m-w-d-Muenchen-Muenchener-Verein-Versicherungsgruppe--13854228-inline.html?rltr=30_5_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Junior-Developer-Java-w-m-d-Frankfurt-am-Main-Cofinpro-AG--13622312-inline.html?rltr=31_6_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Java-Engineer-all-genders-Hamburg-Dresden-Berlin-ParshipMeet-Group--13601926-inline.html?rltr=32_7_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Software-Engineer-Java-Cloud-Microservices-m-w-d-Ottobrunn-bei-Muenchen-IABG-Industrieanlagen-Betriebsgesellschaft-mbH--13725719-inline.html?rltr=33_8_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Java-Fullstack-Entwickler-m-w-d-Berlin-Bremen-Frankfurt-Hamburg-Hannover-Koeln-Muenchen-Reply--13702978-inline.html?rltr=35_10_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Software-Developer-Java-m-w-d-im-Team-Application-Development-and-Modernization-bundesweit-Duesseldorf-Frankfurt-Hamburg-Hannover-Muenchen-Home-Office-x1F-GmbH--13752760-inline.html?rltr=37_12_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Senior-Softwareentwickler-NET-Java-alle-Geschlechter-Bonn-HxGN-Safety-Infrastructure-GmbH-Octave--13816597-inline.html?rltr=40_15_25_seorl_m_0_0_0_0_0_0",
    "https://www.stepstone.de/stellenangebote--Fullstack-Lead-Developer-m-w-d-Java-Muenchen-Hausbank-Muenchen-eG--13877596-inline.html?rltr=43_18_25_seorl_m_0_0_0_0_1_0",
    "https://www.stepstone.de/stellenangebote--Anwendungsentwickler-m-w-d-Java-DevOps-Augsburg-Muenchen-Kassenaerztliche-Vereinigung-Bayerns-KVB--13672743-inline.html?rltr=49_24_25_seorl_m_0_0_0_0_0_0",
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