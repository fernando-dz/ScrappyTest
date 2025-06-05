import asyncio
import json
from playwright.async_api import async_playwright, Error as PlaywrightError


async def scrape_interactive_elements(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto(url)
        except PlaywrightError as e:
            print(f"Error navigating to {url}: {e}")
            await browser.close()
            return None

        # Scrape interactive elements
        try:
            buttons = await page.query_selector_all('button')
            links = await page.query_selector_all('a')
            inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="password"]')

            interactive_elements = {
                'buttons': [await button.inner_text() for button in buttons],
                'links': [await link.get_attribute('href') for link in links],
                'inputs': [await input.get_attribute('placeholder') for input in inputs]
            }
        except Exception as e:
            print(f"Error scraping elements: {e}")
            await browser.close()
            return None

        await browser.close()
        return interactive_elements


def generate_test_cases(elements):
    test_cases = []
    if elements:
        for button in elements['buttons']:
            test_cases.append(f"Test clicking button: {button}")
        for link in elements['links']:
            test_cases.append(f"Test navigating to link: {link}")
        for input_placeholder in elements['inputs']:
            test_cases.append(f"Test input field with placeholder: {input_placeholder}")
    return test_cases


def save_results_to_file(elements, test_cases, filename='results.json'):
    results = {
        'interactive_elements': elements,
        'test_cases': test_cases
    }
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {filename}")


if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    elements = asyncio.run(scrape_interactive_elements(url))
    test_cases = generate_test_cases(elements)

    if elements:
        print("Interactive Elements Found:")
        print(elements)
        print("\nGenerated Test Cases:")
        for case in test_cases:
            print(case)

        # Save results to a file
        save_results_to_file(elements, test_cases)
    else:
        print("No interactive elements found or an error occurred.")