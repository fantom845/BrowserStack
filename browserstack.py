from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def setup_driver():
    """
    Sets up Chrome WebDriver with Spanish language preference.

    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    print("Setting up Chrome WebDriver...")

    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    driver.maximize_window()

    return driver


def navigate_to_elpais(driver) -> None:
    """
    Navigate to El País website and verify it's in Spanish.

    Args:
        driver: WebDriver instance
    """
    print("Navigating to El País...")

    driver.get("https://elpais.com")

    time.sleep(3)

    try:
        # Try multiple common cookie acceptance selectors
        cookie_selectors = [
            "button[aria-label='Accept']",
            "button[id*='accept']",
            "button[class*='accept']",
            "#didomi-notice-agree-button",
            ".didomi-button",
        ]

        for selector in cookie_selectors:
            try:
                accept_button = driver.find_element(By.CSS_SELECTOR, selector)
                accept_button.click()
                print(f"Cookies accepted using selector: {selector}")
                time.sleep(2)
                break
            except:
                continue
        else:
            print("No cookie acceptance button found")
    except Exception as e:
        print(f"Cookie handling failed: {e}")

    print(f"Page title: {driver.title}")

    try:
        from googletrans import Translator

        page_text = driver.find_element(By.TAG_NAME, "body").text

        sample_text = page_text[:500].strip()

        if sample_text:
            print(f"Analyzing text sample: '{sample_text[:100]}...'")

            translator = Translator()

            # Detect language
            detection = translator.detect(sample_text)
            detected_lang = detection.lang

            print(f"Detected language: {detected_lang}")

            if detected_lang == "es":
                print("✓ Website is confirmed to be in Spanish")
            else:
                print(f"⚠ Warning: Website detected as '{detected_lang}', not Spanish")

        else:
            print("⚠ Warning: No text content found for language detection")

    except Exception as e:
        print(f"Language detection failed: {e}")
        print("⚠ Continuing without language verification")


def navigate_to_opinion_section(driver) -> None:

    print("Navigating to Opinion section...")

    # Navigate directly to the Opinion section
    # driver.get("https://elpais.com/opinion")

    try:
        opinion_link = driver.find_element(By.LINK_TEXT, "Opinión")
        opinion_link.click()
    except Exception as e:
        print(f"Failed to navigate to Opinion section: {e}")
        return

    time.sleep(3)

    # Verify we are on the Opinion section
    if "opinion" not in driver.current_url:
        print("Failed to navigate to Opinion section")
        return

    print(f"Current URL: {driver.current_url}")
    print("✓ Successfully navigated to Opinion section")


def get_article_content(driver, article_url):
    """
    Navigate to individual article page and extract full content.
    """
    try: 
        driver.get(article_url)
        time.sleep(3)

        # Extract article content
        content_element = driver.find_element(By.CSS_SELECTOR, "h2")
        content = content_element.text.strip()

        if not content:
            print("⚠ Warning: No content found in article")
            return "No content found"

        driver.get("https://elpais.com/opinion/")
        time.sleep(3)
        return content
    except Exception as e:
        print(f"Error extracting content from {article_url}: {e}")

def get_top_5_articles(driver) -> list:
    driver.get("https://elpais.com/opinion/")
    articles = driver.find_elements(By.TAG_NAME, "article")[:5]
    titles = []
    article_urls = []

    article_data_list = []

    for article in articles:
        try:
            title_element = article.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_element.text
            titles.append(title)
        except:
            title = "Title not found"

        try:
            link_element = article.find_element(By.CSS_SELECTOR, "h2 a")
            article_url = link_element.get_attribute("href")
            article_urls.append(article_url)
        except:
            article_url = "URL not found"

    for i, (title, article_url) in enumerate(zip(titles, article_urls), start=1):
        print(f"{i}. {title} - {article_url}")
        content = get_article_content(driver, article_url)
        article_data = {
            "position": i,
            "title": title,
            "url": article_url,
            "content": content[:500]  # Limit to first 500 characters for preview
        }
        article_data_list.append(article_data)
        
    


    return article_data_list



def main():
    driver = None

    try:
        driver = setup_driver()

        navigate_to_elpais(driver)

        print("Step 1 completed successfully!")

        articles = get_top_5_articles(driver)
        # print in tabular format
        print("\n--- Top 5 Articles in Opinion Section ---")
        print(f"Found {len(articles)} articles in the Opinion section")
        print("Displaying article titles, URLs, and previews:")
        print("\nArticle data:")
        for article in articles:
            print(f"{article['position']}. {article['title']} - {article['url']}")
            print(f"   Content Preview: {article['content'][:100]}...")

        print("Step 2 completed successfully!")

        print("Keeping browser open for 10 seconds...")
        time.sleep(10)  # Keep browser open for 10 seconds to see results

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        if driver:
            driver.quit()
            print("Browser closed.")


if __name__ == "__main__":
    main()
