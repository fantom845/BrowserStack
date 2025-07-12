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

def navigate_to_elpais(driver):
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
            ".didomi-button"
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
        
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        sample_text = page_text[:500].strip()
        
        if sample_text:
            print(f"Analyzing text sample: '{sample_text[:100]}...'")
            
            translator = Translator()
            
            # Detect language
            detection = translator.detect(sample_text)
            detected_lang = detection.lang
            
            print(f"Detected language: {detected_lang}")
            
            if detected_lang == 'es':
                print("✓ Website is confirmed to be in Spanish")
            else:
                print(f"⚠ Warning: Website detected as '{detected_lang}', not Spanish")
                
        else:
            print("⚠ Warning: No text content found for language detection")
            
    except Exception as e:
        print(f"Language detection failed: {e}")
        print("⚠ Continuing without language verification")


        

def navigate_to_opinion_section(driver):

    print("Navigating to Opinion section...")

    # Navigate directly to the Opinion section
    #driver.get("https://elpais.com/opinion")
    
    try:
        opinion_link = driver.find_element(By.LINK_TEXT, "Opinión")
        opinion_link.click()
    except Exception as e:
        print(f"Failed to navigate to Opinion section: {e}")
        return
    
    time.sleep(3)


    time.sleep(3)

    print(f"Opinion section title: {driver.title}")
    print("✓ Successfully navigated to Opinion section")

    
def explore_page_structure(driver):
    """
    Explore the page structure to understand how articles are organized.
    """
    print("\n--- Exploring Page Structure ---")
    
    article_links = driver.find_elements(By.TAG_NAME, "article")
    print(f"Found {len(article_links)} <article> elements")
    
    all_links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Found {len(all_links)} total links on the page")
    
    h2_elements = driver.find_elements(By.TAG_NAME, "h2")
    h3_elements = driver.find_elements(By.TAG_NAME, "h3")
    
    print(f"Found {len(h2_elements)} <h2> elements (likely article titles)")
    print(f"Found {len(h3_elements)} <h3> elements (possibly article titles)")
    
    print("\n--- Article Titles ---")
    for i, h2 in enumerate(h2_elements[:5]):
        try:
            title_text = h2.text.strip()
            if title_text:
                print(f"{i+1}. {title_text}")
        except Exception as e:
            print(f"{i+1}. [Could not extract text: {e}]")


def main():
    driver = None
    
    try:
        driver = setup_driver()
        
        navigate_to_elpais(driver)
        
        print("Step 1 completed successfully!")

        navigate_to_opinion_section(driver)
        explore_page_structure(driver)
        

        print("Step 2 completed successfully!")

        time.sleep(10)  # Keep browser open for 10 seconds to see results
        print("Keeping browser open for 10 seconds...")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()