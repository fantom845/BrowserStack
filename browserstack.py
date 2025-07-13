from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import os
import re


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

    if "opinion" not in driver.current_url:
        print("Failed to navigate to Opinion section")
        return

    print(f"Current URL: {driver.current_url}")
    print("✓ Successfully navigated to Opinion section")


def get_article_content(driver):
    """
    Navigate to individual article page and extract full content.
    """
    try:
        # Check if article is paywalled
        is_paywalled = False
        try:
            driver.find_element(By.CSS_SELECTOR, "#ctn_freemium_article")
            is_paywalled = True
            print("🔒 Detected paywalled article")
        except:
            print("📖 Non-paywalled article")

        collected_content = []

        if is_paywalled:
            # Step 1: Get teaser content (visible content)
            teaser_content = []
            try:
                teaser_elements = driver.find_elements(By.CSS_SELECTOR, "div.a_c p")
                for elem in teaser_elements:
                    text = elem.text.strip()
                    if text and len(text) > 20:
                        teaser_content.append(text)
                print(f"📖 Found {len(teaser_content)} teaser paragraphs")
            except:
                pass

            # Step 2: Try to make paywall content visible using JavaScript
            try:
                driver.execute_script(
                    """
                    // Remove display: none from paywall content
                    var hiddenElements = document.querySelectorAll('.a_b_wall._dn, ._dn');
                    hiddenElements.forEach(function(element) {
                        element.style.display = 'block';
                        element.style.visibility = 'visible';
                        element.classList.remove('_dn');
                    });
                """
                )
                time.sleep(1)
                print("💡 Attempted to make paywall content visible")
            except Exception as e:
                print(f"Could not execute script: {e}")

            # Step 3: Extract paywall content (now hopefully visible)
            paywall_content = []
            paywall_selectors = [
                "div.a_b_wall p",
                "#main-content > div.a_c.clearfix > div:nth-child(5) p",
                "div.a_b_wall._dn p",
                ".a_b_wall p",
            ]

            for selector in paywall_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        new_content = []
                        for elem in elements:
                            text = elem.text.strip()
                            # Only add if not already in teaser and meaningful length
                            if (
                                text
                                and len(text) > 20
                                and text not in " ".join(teaser_content)
                            ):
                                new_content.append(text)

                        if new_content:
                            paywall_content.extend(new_content)
                            print(
                                f"🔒 Found {len(new_content)} paywall paragraphs with selector: {selector}"
                            )
                            break  # Stop at first successful paywall extraction
                except:
                    continue

            # Step 4: Combine teaser + paywall content
            all_content = teaser_content + paywall_content
            if all_content:
                final_content = " ".join(all_content)
                print(
                    f"🔒 Combined article: {len(teaser_content)} teaser + {len(paywall_content)} paywall = {len(all_content)} total paragraphs, {len(final_content)} characters"
                )
                return final_content

        else:
            # For non-paywalled articles: use original logic
            content_selectors = [
                "div.a_c p",
                "[data-dtm-region='articulo_cuerpo'] p",
                "#main-content > div.a_c.clearfix > p",
                "article p",
                ".articulo-contenido p",
                "h2",  # Fallback
            ]

            for selector in content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        content = " ".join(
                            [elem.text.strip() for elem in elements[:5]]
                        )  # First 5 paragraphs
                        if content and len(content) > 200:
                            print(
                                f"Found {len(elements)} paragraphs with selector: {selector}"
                            )
                            print(f"Total content length: {len(content)} characters")
                            return content
                except:
                    continue

        print("⚠ Warning: No content found in article")
        return "No content found"

    except Exception as e:
        print(f"Error extracting content from {driver.current_url}: {e}")
        return "No content found"


def download_image(image_url, filename, folder="images"):
    """
    Download an image from URL and save it locally.
    """
    try:
        # Create images directory
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

        # Clean filename
        safe_filename = re.sub(r'[<>:"/\|?*]', "_", filename)
        safe_filename = safe_filename[:50]  # Limit length

        if image_url.endswith(".jpg") or image_url.endswith(".jpeg"):
            extension = ".jpg"
        elif image_url.endswith(".png"):
            extension = ".png"
        elif image_url.endswith(".webp"):
            extension = ".webp"
        else:
            extension = ".jpg"

        full_filename = f"{safe_filename}{extension}"
        local_path = os.path.join(folder, full_filename)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"📸 Image saved: {local_path}")
        return local_path

    except Exception as e:
        print(f"Failed to download image: {e}")
        return None


def save_cover_image(driver, article_title):
    """
    Find and download the cover image for the current article.
    """
    image_selectors = [
        "//*[@id='main-content']/header/div[2]/figure/span/img",
        "//figure//img",
        "//header//img",
        "//article//img[1]",
        "//img[contains(@class, 'article')]",
    ]

    for selector in image_selectors:
        try:
            image_element = driver.find_element(By.XPATH, selector)
            image_url = image_element.get_attribute("src")

            if image_url and image_url.startswith("http"):
                print(f"📸 Found cover image: {image_url}")

                # Try to get caption for filename
                try:
                    caption_element = driver.find_element(
                        By.XPATH,
                        "//*[@id='main-content']/header/div[2]/figure/figcaption",
                    )
                    filename = caption_element.text[:30]
                except:
                    filename = article_title[:30]

                if not filename.strip():
                    filename = f"article_image_{int(time.time())}"

                local_path = download_image(image_url, filename)
                return local_path

        except Exception as e:
            continue

    print("⚠ No cover image found")
    return None


def get_top_5_articles(driver) -> list:
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
        driver.get(article_url)
        time.sleep(3)
        content = get_article_content(driver)

        # Download cover image
        image_path = save_cover_image(driver, title)

        article_data = {
            "position": i,
            "title": title,
            "url": article_url,
            "content": content,
            "cover_image_path": image_path,
        }
        article_data_list.append(article_data)

    return article_data_list


def main():
    driver = None

    try:
        driver = setup_driver()

        navigate_to_elpais(driver)

        print("Step 1 completed successfully!")

        navigate_to_opinion_section(driver)
        articles = get_top_5_articles(driver)
        # print in tabular format
        print("\n--- Top 5 Articles in Opinion Section ---")
        print(f"Found {len(articles)} articles in the Opinion section")
        print("Displaying article titles, URLs, and previews:")
        print("\nArticle data:")
        for article in articles:
            print(f"{article['position']}. {article['title']} - {article['url']}")
            print(f"   Content Preview: {article['content']}\n")

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
