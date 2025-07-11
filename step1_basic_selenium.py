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
    chrome_options.add_argument("--lang=es")
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
            confidence = detection.confidence
            
            print(f"Detected language: {detected_lang}")
            
            if confidence is not None:
                print(f"Confidence: {confidence:.2f}")
            else:
                print("Confidence: Not available")
            
            if detected_lang == 'es':
                print("✓ Website is confirmed to be in Spanish")
            else:
                print(f"⚠ Warning: Website detected as '{detected_lang}', not Spanish")
                
        else:
            print("⚠ Warning: No text content found for language detection")
            
    except Exception as e:
        print(f"Language detection failed: {e}")
        print("⚠ Continuing without language verification")



def main():
    driver = None
    
    try:
        driver = setup_driver()
        
        navigate_to_elpais(driver)
        
        print("Step 1 completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()