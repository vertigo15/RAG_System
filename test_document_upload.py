"""
Selenium test to debug PDF upload functionality in the Documents page.
"""

import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def test_pdf_upload():
    """Test PDF file upload functionality"""
    
    # Setup Chrome driver with options
    options = webdriver.ChromeOptions()
    # Comment out headless if you want to see the browser
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Navigate to the application
        print("Navigating to Documents page...")
        driver.get("http://localhost:3100/documents")
        time.sleep(2)
        
        # Take screenshot of initial state
        driver.save_screenshot("screenshots/1_initial_page.png")
        print("Screenshot saved: 1_initial_page.png")
        
        # Check if page loaded correctly
        try:
            page_title = wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Documents')]"))
            )
            print(f"✅ Page title found: {page_title.text}")
        except TimeoutException:
            print("❌ Page title not found - page may not have loaded")
            driver.save_screenshot("screenshots/error_page_not_loaded.png")
            return
        
        # Find the file input element
        print("\nLooking for file input element...")
        try:
            file_input = driver.find_element(By.ID, "file-upload")
            print(f"✅ File input found: {file_input.get_attribute('type')}")
            print(f"   - Accept attribute: {file_input.get_attribute('accept')}")
            print(f"   - Multiple: {file_input.get_attribute('multiple')}")
            print(f"   - Disabled: {file_input.get_attribute('disabled')}")
            print(f"   - Class: {file_input.get_attribute('class')}")
        except NoSuchElementException:
            print("❌ File input element not found")
            driver.save_screenshot("screenshots/error_no_file_input.png")
            return
        
        # Check for Upload button
        print("\nLooking for Upload button...")
        try:
            upload_label = driver.find_element(By.CSS_SELECTOR, "label[for='file-upload']")
            print(f"✅ Upload button label found")
            print(f"   - Text: {upload_label.text}")
            print(f"   - Cursor: {upload_label.value_of_css_property('cursor')}")
            driver.save_screenshot("screenshots/2_upload_button_found.png")
        except NoSuchElementException:
            print("❌ Upload button label not found")
        
        # Prepare test PDF file from Downloads
        downloads_path = Path.home() / "Downloads"
        print(f"\nLooking for PDF files in: {downloads_path}")
        
        # Find any PDF file in Downloads
        pdf_files = list(downloads_path.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in Downloads folder")
            print("   Creating a test PDF file...")
            
            # Create a simple test PDF if none exists
            test_pdf_path = downloads_path / "test_upload.pdf"
            try:
                from reportlab.pdfgen import canvas
                c = canvas.Canvas(str(test_pdf_path))
                c.drawString(100, 750, "Test PDF for Upload")
                c.save()
                pdf_file_path = test_pdf_path
                print(f"✅ Created test PDF: {pdf_file_path}")
            except ImportError:
                print("   reportlab not installed, creating dummy PDF...")
                # Create a minimal PDF structure
                with open(test_pdf_path, 'wb') as f:
                    f.write(b'%PDF-1.4\n')
                pdf_file_path = test_pdf_path
        else:
            pdf_file_path = pdf_files[0]
            print(f"✅ Found PDF file: {pdf_file_path.name}")
        
        # Check if file exists and is readable
        if not pdf_file_path.exists():
            print(f"❌ PDF file does not exist: {pdf_file_path}")
            return
        
        print(f"   - File size: {pdf_file_path.stat().st_size / 1024:.2f} KB")
        print(f"   - Absolute path: {pdf_file_path.absolute()}")
        
        # Try to upload the file
        print("\nAttempting to upload file...")
        try:
            # Send file path to hidden input
            file_input.send_keys(str(pdf_file_path.absolute()))
            print("✅ File path sent to input element")
            time.sleep(1)
            
            driver.save_screenshot("screenshots/3_after_file_selected.png")
            
            # Wait for upload to start (spinner should appear)
            try:
                spinner = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".spinner, [role='status']"))
                )
                print("✅ Upload started (spinner detected)")
                driver.save_screenshot("screenshots/4_upload_in_progress.png")
                
                # Wait for upload to complete (spinner disappears)
                wait.until(EC.invisibility_of_element(spinner))
                print("✅ Upload completed (spinner disappeared)")
                time.sleep(2)
                
            except TimeoutException:
                print("⚠️  No spinner detected - upload may be instant or failed")
            
            driver.save_screenshot("screenshots/5_after_upload.png")
            
            # Check for success/error messages
            print("\nChecking for toast messages...")
            try:
                toast = driver.find_element(By.CSS_SELECTOR, ".toast, .notification, [role='alert']")
                print(f"✅ Toast message found: {toast.text}")
            except NoSuchElementException:
                print("⚠️  No toast message found")
            
            # Check if document appears in the table
            print("\nChecking document table...")
            try:
                table = driver.find_element(By.TAG_NAME, "table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"✅ Table found with {len(rows)} rows")
                
                # Look for the uploaded file
                for row in rows:
                    if pdf_file_path.name in row.text:
                        print(f"✅ Uploaded document found in table: {pdf_file_path.name}")
                        break
                else:
                    print(f"⚠️  Uploaded document not found in table yet")
                    
            except NoSuchElementException:
                print("❌ Document table not found")
            
            driver.save_screenshot("screenshots/6_final_state.png")
            
        except Exception as e:
            print(f"❌ Error during file upload: {str(e)}")
            driver.save_screenshot("screenshots/error_upload_failed.png")
            raise
        
        # Check browser console for errors
        print("\nChecking browser console logs...")
        logs = driver.get_log('browser')
        if logs:
            print("Console logs:")
            for log in logs:
                level = log['level']
                message = log['message']
                if level in ['SEVERE', 'ERROR']:
                    print(f"   ❌ {level}: {message}")
                elif level == 'WARNING':
                    print(f"   ⚠️  {level}: {message}")
                else:
                    print(f"   ℹ️  {level}: {message}")
        else:
            print("   No console logs found")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        driver.save_screenshot("screenshots/error_general.png")
        raise
    
    finally:
        # Keep browser open for manual inspection
        print("\nPress Enter to close browser...")
        input()
        driver.quit()


if __name__ == "__main__":
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)
    
    print("=" * 60)
    print("PDF Upload Test - RAG System")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Open the Documents page")
    print("2. Locate a PDF file from Downloads folder")
    print("3. Attempt to upload the file")
    print("4. Check for success/error messages")
    print("5. Take screenshots at each step")
    print("\nScreenshots will be saved in: ./screenshots/")
    print("=" * 60)
    
    test_pdf_upload()
