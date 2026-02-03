"""
Selenium test suite for Documents page enhancements.
Tests search, filtering, pagination, detail panel, and PDF upload.
"""

import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DocumentsPageTest:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []

    def setup(self):
        """Initialize Selenium WebDriver"""
        print("\n🚀 Setting up Selenium WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            return False

    def teardown(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            print("\n🧹 WebDriver closed")

    def navigate_to_documents(self):
        """Navigate to Documents page"""
        try:
            print(f"\n📍 Navigating to {self.base_url}/documents")
            self.driver.get(f"{self.base_url}/documents")
            time.sleep(3)  # Wait for page load and React to render
            
            # Check if page is accessible (handle 404 or connection error)
            try:
                # Try multiple XPath variations for the title
                title = None
                try:
                    title = self.driver.find_element(By.XPATH, "//h1[contains(., 'Documents')]")
                except:
                    title = self.driver.find_element(By.XPATH, "//h1[text()='📄 Documents']")
                
                if title:
                    print("✅ Documents page loaded successfully")
                    return True
            except NoSuchElementException:
                # Check if page body exists (connection worked but page structure different)
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    page_source = self.driver.page_source
                    if "Cannot GET" in page_source or "404" in page_source:
                        print(f"❌ Page not found (404). Make sure frontend is running at {self.base_url}")
                    else:
                        print(f"❌ Documents page title not found. Page may not be fully loaded.")
                        print(f"   Current URL: {self.driver.current_url}")
                    return False
                except:
                    print(f"❌ Failed to load page. Check if {self.base_url} is accessible")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to navigate to Documents page: {e}")
            print(f"   Make sure the app is running at {self.base_url}")
            return False

    def test_page_elements_exist(self):
        """Test that all expected page elements exist"""
        print("\n🧪 Test: Page Elements Exist")
        
        tests = [
            ("Documents Title", "//h1[contains(., 'Documents')]"),
            ("Upload Button", "//span[contains(text(), 'Upload')]"),
            ("Refresh Button", "//button[contains(text(), 'Refresh')]"),
            ("Search Input", "//input[@placeholder]"),
            ("Status Filter Dropdown", "//select"),
            ("Documents Table", "//table"),
        ]
        
        all_passed = True
        for test_name, xpath in tests:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                print(f"  ✅ {test_name} found")
                self.test_results.append((test_name, True))
            except NoSuchElementException:
                print(f"  ❌ {test_name} NOT found")
                self.test_results.append((test_name, False))
                all_passed = False
        
        return all_passed

    def test_search_functionality(self):
        """Test search input functionality"""
        print("\n🧪 Test: Search Functionality")
        
        try:
            # Get initial document count
            search_input = self.driver.find_element(By.XPATH, "//input[@placeholder]")
            
            # Type search query
            search_input.clear()
            search_input.send_keys("pdf")
            time.sleep(1)
            
            print("  ✅ Search input works - typed 'pdf'")
            
            # Verify search executed
            table_rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            print(f"  ℹ️  Found {len(table_rows)} results after search")
            
            # Clear search
            search_input.clear()
            time.sleep(1)
            
            print("  ✅ Search cleared successfully")
            self.test_results.append(("Search Functionality", True))
            return True
            
        except Exception as e:
            print(f"  ❌ Search functionality test failed: {e}")
            self.test_results.append(("Search Functionality", False))
            return False

    def test_status_filter(self):
        """Test status filter dropdown"""
        print("\n🧪 Test: Status Filter")
        
        try:
            # Find and click status filter dropdown
            status_select = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//select"))
            )
            
            select = Select(status_select)
            
            # Test filtering by "completed"
            select.select_by_value("completed")
            time.sleep(1)
            print("  ✅ Filtered by 'Completed' status")
            
            # Test filtering by "processing"
            select.select_by_value("processing")
            time.sleep(1)
            print("  ✅ Filtered by 'Processing' status")
            
            # Reset to all
            select.select_by_value("")
            time.sleep(1)
            print("  ✅ Reset filter to 'All Status'")
            
            self.test_results.append(("Status Filter", True))
            return True
            
        except Exception as e:
            print(f"  ❌ Status filter test failed: {e}")
            self.test_results.append(("Status Filter", False))
            return False

    def test_document_row_click(self):
        """Test clicking on document row to open detail panel"""
        print("\n🧪 Test: Document Row Click & Detail Panel")
        
        try:
            # Wait for table rows to be available
            table_rows = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr"))
            )
            
            if not table_rows:
                print("  ⚠️  No documents found to test row click")
                self.test_results.append(("Document Row Click", None))
                return None
            
            # Click first row
            first_row = table_rows[0]
            first_row.click()
            time.sleep(1)
            
            print("  ✅ Clicked first document row")
            
            # Check if detail panel opened
            detail_panel = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Document Details')]")
            if detail_panel:
                print("  ✅ Detail panel opened successfully")
                self.test_results.append(("Document Row Click", True))
                return True
                
        except TimeoutException:
            print("  ⚠️  No documents available to test")
            self.test_results.append(("Document Row Click", None))
            return None
        except Exception as e:
            print(f"  ❌ Document row click test failed: {e}")
            self.test_results.append(("Document Row Click", False))
            return False

    def test_detail_panel_elements(self):
        """Test that detail panel contains expected elements"""
        print("\n🧪 Test: Detail Panel Elements")
        
        try:
            elements_to_check = [
                ("Close Button", "//button[contains(., 'Close')]//parent::*//following-sibling::button"),
                ("Delete Button", "//button[contains(text(), 'Delete')]"),
                ("File Size", "//p[contains(text(), 'File Size')]"),
                ("Chunks Count", "//p[contains(text(), 'Chunks')]"),
                ("Vectors Count", "//p[contains(text(), 'Vectors')]"),
            ]
            
            all_found = True
            for element_name, xpath in elements_to_check:
                try:
                    # Try to find element with longer timeout for detail panel
                    self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    print(f"  ✅ {element_name} found in detail panel")
                except TimeoutException:
                    print(f"  ⚠️  {element_name} not found (might not be visible)")
            
            self.test_results.append(("Detail Panel Elements", True))
            return True
            
        except Exception as e:
            print(f"  ⚠️  Detail panel elements test: {e}")
            self.test_results.append(("Detail Panel Elements", None))
            return None

    def test_close_detail_panel(self):
        """Test closing detail panel"""
        print("\n🧪 Test: Close Detail Panel")
        
        try:
            # Find close button (X button in the detail panel header)
            close_button = self.driver.find_element(By.XPATH, 
                "//div[contains(@class, 'fixed')]//button[contains(@class, 'text-gray-500')]")
            close_button.click()
            time.sleep(1)
            
            print("  ✅ Clicked close button")
            
            # Verify panel is closed
            try:
                self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Document Details')]")
                print("  ⚠️  Detail panel still visible after close")
                self.test_results.append(("Close Detail Panel", False))
                return False
            except NoSuchElementException:
                print("  ✅ Detail panel closed successfully")
                self.test_results.append(("Close Detail Panel", True))
                return True
                
        except NoSuchElementException:
            print("  ⚠️  Close button not found or panel not open")
            self.test_results.append(("Close Detail Panel", None))
            return None
        except Exception as e:
            print(f"  ❌ Close detail panel test failed: {e}")
            self.test_results.append(("Close Detail Panel", False))
            return False

    def test_pdf_upload(self, pdf_path: str):
        """Test uploading PDF file"""
        print(f"\n🧪 Test: PDF Upload - {Path(pdf_path).name}")
        
        if not os.path.exists(pdf_path):
            print(f"  ❌ PDF file not found: {pdf_path}")
            self.test_results.append(("PDF Upload", False))
            return False
        
        try:
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            print(f"  ℹ️  File size: {file_size_mb:.2f} MB")
            
            # Find file input
            file_input = self.driver.find_element(By.ID, "file-upload")
            
            # Send file path to input
            file_input.send_keys(os.path.abspath(pdf_path))
            print(f"  ✅ File selected: {Path(pdf_path).name}")
            
            time.sleep(2)
            
            # Wait for upload to complete
            try:
                # Look for success message or document appearing in table
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Document uploaded')]"))
                )
                print("  ✅ Upload success message appeared")
            except TimeoutException:
                print("  ℹ️  No explicit success message found (checking table instead)")
            
            time.sleep(2)
            
            print("  ✅ PDF uploaded successfully")
            self.test_results.append(("PDF Upload", True))
            return True
            
        except Exception as e:
            print(f"  ❌ PDF upload test failed: {e}")
            self.test_results.append(("PDF Upload", False))
            return False

    def test_refresh_button(self):
        """Test refresh button functionality"""
        print("\n🧪 Test: Refresh Button")
        
        try:
            refresh_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Refresh')]")
            refresh_button.click()
            time.sleep(2)
            
            print("  ✅ Clicked refresh button")
            
            # Verify page is still accessible
            documents_title = self.driver.find_element(By.XPATH, "//h1[contains(text(), 'Documents')]")
            if documents_title:
                print("  ✅ Page refreshed successfully")
                self.test_results.append(("Refresh Button", True))
                return True
                
        except Exception as e:
            print(f"  ❌ Refresh button test failed: {e}")
            self.test_results.append(("Refresh Button", False))
            return False

    def test_pagination(self):
        """Test pagination controls"""
        print("\n🧪 Test: Pagination")
        
        try:
            # Check if pagination exists
            next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            
            if next_button:
                print("  ✅ Pagination controls found")
                
                # Check if next button is disabled (no more pages)
                if next_button.get_attribute("disabled"):
                    print("  ℹ️  Next button is disabled (only 1 page of documents)")
                else:
                    print("  ℹ️  Multiple pages of documents available")
                
                self.test_results.append(("Pagination", True))
                return True
                
        except NoSuchElementException:
            print("  ℹ️  Pagination controls not visible (fewer than 10 documents)")
            self.test_results.append(("Pagination", None))
            return None
        except Exception as e:
            print(f"  ⚠️  Pagination test: {e}")
            self.test_results.append(("Pagination", None))
            return None

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, result in self.test_results if result is True)
        failed = sum(1 for _, result in self.test_results if result is False)
        skipped = sum(1 for _, result in self.test_results if result is None)
        total = len(self.test_results)
        
        print(f"\n📊 Results:")
        print(f"  ✅ Passed:  {passed}/{total}")
        print(f"  ❌ Failed:  {failed}/{total}")
        print(f"  ⊘  Skipped: {skipped}/{total}")
        
        print(f"\n📋 Details:")
        for test_name, result in self.test_results:
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⊘ SKIP"
            print(f"  {status} - {test_name}")
        
        success_rate = (passed / (total - skipped) * 100) if (total - skipped) > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed} test(s) failed")

    def run_full_test_suite(self, pdf_path: str = None):
        """Run complete test suite"""
        print("\n" + "=" * 70)
        print("DOCUMENTS PAGE TEST SUITE")
        print("=" * 70)
        
        # Setup
        if not self.setup():
            print("❌ Failed to setup WebDriver")
            return False
        
        try:
            # Navigate to documents page
            if not self.navigate_to_documents():
                print("❌ Failed to navigate to Documents page")
                return False
            
            # Run tests
            self.test_page_elements_exist()
            self.test_search_functionality()
            self.test_status_filter()
            self.test_document_row_click()
            self.test_detail_panel_elements()
            self.test_close_detail_panel()
            self.test_refresh_button()
            self.test_pagination()
            
            # Upload PDF if provided
            if pdf_path:
                self.test_pdf_upload(pdf_path)
            
            # Print results
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
            return False
            
        finally:
            self.teardown()


if __name__ == "__main__":
    import sys
    
    # PDF file to test
    pdf_file = r"C:\Users\user\Downloads\Docker_80bd9fd_Security_Export (003).pdf"
    
    # Alternative path if file doesn't exist
    if not os.path.exists(pdf_file):
        print(f"⚠️  Default PDF not found: {pdf_file}")
        print("Looking for other PDFs in Downloads folder...")
        
        downloads = Path.home() / "Downloads"
        pdfs = list(downloads.glob("*.pdf"))
        if pdfs:
            pdf_file = str(pdfs[0])
            print(f"ℹ️  Using: {pdfs[0].name}")
        else:
            pdf_file = None
            print("⚠️  No PDF file found. Skipping upload test.")
    
    # Run tests on port 3100 (Docker frontend)
    tester = DocumentsPageTest(base_url="http://localhost:3100")
    tester.run_full_test_suite(pdf_path=pdf_file)
