from playwright.sync_api import sync_playwright
import json
import time

def scrape_ieee(topic):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://ieeexplore.ieee.org/Xplore/home.jsp')

        # Esperar que el campo de búsqueda esté disponible
        page.wait_for_selector('input[type="search"]', timeout=60000)

        # Buscar el tema especificado
        page.fill('input[type="search"]', topic)
        page.click('button[type="submit"]')

        page.wait_for_selector('.facet-ctype-options', timeout=60000)

        # Marcar las casillas de "Journals" y "Conferences"
        page.check('input[id="refinement-ContentType:Journals"]')
        page.check('input[id="refinement-ContentType:Conferences"]')

        # Esperar a que se carguen los filtros y marcar "Open Access Only"
        page.wait_for_selector('.filter-box-content-options', timeout=60000)
        open_access_radio = page.query_selector('input[type="radio"] ~ span.text-nowrap:has-text("Open Access Only")')
        if open_access_radio:
            open_access_radio.click()
        
        # Aplicar los filtros
        page.click('button[type="submit"]')

        page.wait_for_selector('.List-results-items', timeout=60000)

        papers = []

        def scrape_page():
            for paper in page.query_selector_all('.List-results-items '):
                try:
                    title_element = paper.query_selector('h3 a.fw-bold')
                    authors_elements = paper.query_selector_all('xpl-authors-name-list p.author span.text-base-md-lh')
                    pdf_link_element = paper.query_selector('a[aria-label="PDF"][tooltipclass="document-toolbar-tooltip"]')
                    abstract_element = paper.query_selector('div.js-displayer-content span[xplhighlight]')

                    title = title_element.inner_text() if title_element else 'No title available'
                    authors = '; '.join([author.inner_text() for author in authors_elements]) if authors_elements else 'No authors available'
                    
                    # Obtener el enlace al PDF
                    pdf_link = pdf_link_element.get_attribute('href') if pdf_link_element else 'No PDF link available'
                    if pdf_link != 'No PDF link available':
                        pdf_link = f'https://ieeexplore.ieee.org{pdf_link}'

                    # Obtener el abstract
                    abstract = abstract_element.inner_text() if abstract_element else 'No abstract available'

                    papers.append({
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'pdf_link': pdf_link,
                        
                    })
                except Exception as e:
                    print(f"Error processing paper: {e}")

        while True:
            scrape_page()
            next_button = page.query_selector('li.next-btn button')
            if next_button and next_button.is_enabled():
                next_button.click()
                time.sleep(2) 
                page.wait_for_selector('.List-results-items', timeout=60000)
            else:
                break

        browser.close()
        return papers

if __name__ == "__main__":
    topic = "person re-identification"
    papers = scrape_ieee(topic)
    with open('data/papers.json', 'w') as f:
        json.dump(papers, f, indent=4)
