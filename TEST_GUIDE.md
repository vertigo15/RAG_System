# Documents Page Test Guide

## Prerequisites

### 1. Dependencies
Ensure all required packages are installed:

```bash
pip install -r test_requirements.txt
```

Required packages:
- `selenium>=4.0.0` - Web automation framework
- `webdriver-manager>=4.0.0` - Automatic ChromeDriver management
- `reportlab>=3.6.0` - PDF generation

### 2. Application Running
Make sure the RAG System is running:

```bash
# From project root
docker-compose up
```

The frontend should be accessible at: `http://localhost:3000`

### 3. PDF Test File
The test will look for: `C:\Users\user\Downloads\Docker_80bd9fd_Security_Export (003).pdf`

If this file is not found, the test will:
1. Look for any PDF in the Downloads folder
2. Skip the PDF upload test if none are found

## Running the Tests

### Option 1: Run Full Test Suite (Recommended)

```bash
python test_documents_page.py
```

This will:
1. Initialize Selenium WebDriver
2. Navigate to the Documents page
3. Run all test cases
4. Upload the PDF file
5. Generate a comprehensive test report

### Option 2: Run from Python REPL

```python
from test_documents_page import DocumentsPageTest

tester = DocumentsPageTest(base_url="http://localhost:3000")
tester.run_full_test_suite(pdf_path=r"C:\Users\user\Downloads\Docker_80bd9fd_Security_Export (003).pdf")
```

### Option 3: Run Specific Tests

```python
from test_documents_page import DocumentsPageTest

tester = DocumentsPageTest()
tester.setup()
tester.navigate_to_documents()
tester.test_search_functionality()
tester.test_status_filter()
tester.teardown()
```

## Test Cases

The test suite includes the following test cases:

### 1. **Page Elements Exist** ✅
- Documents Title
- Upload Button
- Refresh Button
- Search Input
- Status Filter Dropdown
- Documents Table

### 2. **Search Functionality** 🔍
- Types search query in search input
- Verifies results filter in real-time
- Clears search to reset results

### 3. **Status Filter** 🔽
- Tests filtering by "Completed" status
- Tests filtering by "Processing" status
- Tests resetting to "All Status"

### 4. **Document Row Click** 🖱️
- Clicks first document row
- Verifies detail panel opens
- Confirms panel shows "Document Details" title

### 5. **Detail Panel Elements** 📋
- Verifies Close Button exists
- Verifies Delete Button exists
- Verifies File Size display
- Verifies Chunks Count display
- Verifies Vectors Count display

### 6. **Close Detail Panel** ✕
- Clicks close button
- Verifies panel closes
- Confirms detail panel is no longer visible

### 7. **Refresh Button** 🔄
- Clicks refresh button
- Waits for page refresh
- Verifies page is still accessible

### 8. **Pagination** 📄
- Checks for pagination controls
- Verifies Next button exists
- Checks if Next button is disabled (indicates single page)

### 9. **PDF Upload** 📤
- Locates the PDF file
- Selects file in file input
- Waits for upload to complete
- Verifies success

## Expected Output

### Successful Test Run:

```
======================================================================
DOCUMENTS PAGE TEST SUITE
======================================================================

🚀 Setting up Selenium WebDriver...
✅ WebDriver initialized successfully

📍 Navigating to http://localhost:3000/documents
✅ Documents page loaded successfully

🧪 Test: Page Elements Exist
  ✅ Documents Title found
  ✅ Upload Button found
  ✅ Refresh Button found
  ✅ Search Input found
  ✅ Status Filter Dropdown found
  ✅ Documents Table found

🧪 Test: Search Functionality
  ✅ Search input works - typed 'pdf'
  ℹ️  Found 5 results after search
  ✅ Search cleared successfully

🧪 Test: Status Filter
  ✅ Filtered by 'Completed' status
  ✅ Filtered by 'Processing' status
  ✅ Reset filter to 'All Status'

🧪 Test: Document Row Click & Detail Panel
  ✅ Clicked first document row
  ✅ Detail panel opened successfully

🧪 Test: Detail Panel Elements
  ✅ Close Button found in detail panel
  ✅ Delete Button found in detail panel
  ✅ File Size found in detail panel
  ✅ Chunks Count found in detail panel
  ✅ Vectors Count found in detail panel

🧪 Test: Close Detail Panel
  ✅ Clicked close button
  ✅ Detail panel closed successfully

🧪 Test: Refresh Button
  ✅ Clicked refresh button
  ✅ Page refreshed successfully

🧪 Test: Pagination
  ✅ Pagination controls found
  ℹ️  Multiple pages of documents available

🧪 Test: PDF Upload - Docker_80bd9fd_Security_Export (003).pdf
  ℹ️  File size: 2.45 MB
  ✅ File selected: Docker_80bd9fd_Security_Export (003).pdf
  ✅ Upload success message appeared
  ✅ PDF uploaded successfully

======================================================================
TEST SUMMARY
======================================================================

📊 Results:
  ✅ Passed:  17/17
  ❌ Failed:  0/17
  ⊘  Skipped: 0/17

📋 Details:
  ✅ PASS - Documents Title
  ✅ PASS - Upload Button
  ✅ PASS - Refresh Button
  ✅ PASS - Search Input
  ✅ PASS - Status Filter Dropdown
  ✅ PASS - Documents Table
  ✅ PASS - Search Functionality
  ✅ PASS - Status Filter
  ✅ PASS - Document Row Click
  ✅ PASS - Detail Panel Elements
  ✅ PASS - Close Detail Panel
  ✅ PASS - Refresh Button
  ✅ PASS - Pagination
  ✅ PASS - PDF Upload

📈 Success Rate: 100%

🎉 All tests passed!

🧹 WebDriver closed
```

## Troubleshooting

### Issue: "Failed to initialize WebDriver"

**Solution:**
```bash
pip install --upgrade webdriver-manager selenium
```

### Issue: "Documents page not found (404)"

**Solution:**
- Verify frontend is running: `http://localhost:3000`
- Check Docker containers: `docker-compose ps`
- Restart services: `docker-compose restart`

### Issue: "No PDF file found"

**Solution:**
- Place PDF in: `C:\Users\user\Downloads\`
- Or modify the `pdf_file` path in the test script

### Issue: "Element not interactable"

**Solution:**
- Increase wait time in code: `time.sleep(3)` instead of `1`
- Or modify `WebDriverWait` timeout: `WebDriverWait(driver, 20)` instead of `10`

### Issue: "Chrome driver error"

**Solution:**
```bash
# Clear webdriver cache
rm -r ~/.wdm  # Linux/Mac
rmdir /s %USERPROFILE%\.wdm  # Windows

# Reinstall
pip install --force-reinstall webdriver-manager
```

## Test Execution Time

Typical test run duration: **2-5 minutes**

Breakdown:
- Setup: 30 seconds
- Navigation: 2 seconds
- Page elements: 5 seconds
- Search test: 3 seconds
- Filter test: 3 seconds
- Row click: 2 seconds
- Detail panel: 2 seconds
- Close panel: 2 seconds
- Refresh: 2 seconds
- Pagination: 1 second
- PDF upload: 30-120 seconds (depends on file size)
- Teardown: 1 second

## Advanced Usage

### Running Headless (No GUI)

```python
from test_documents_page import DocumentsPageTest
from selenium.webdriver.chrome.options import Options

tester = DocumentsPageTest()
# Modify setup to use headless mode
options = Options()
options.add_argument("--headless")
# ... rest of setup
```

### Custom Base URL

```python
tester = DocumentsPageTest(base_url="http://custom-domain:3000")
tester.run_full_test_suite()
```

### Skipping PDF Upload

```python
tester = DocumentsPageTest()
tester.run_full_test_suite(pdf_path=None)
```

### Adding Custom Tests

```python
def test_custom_feature(self):
    """Your custom test"""
    try:
        # Your test code here
        self.test_results.append(("Custom Feature", True))
    except Exception as e:
        self.test_results.append(("Custom Feature", False))

# Add to run_full_test_suite
tester.test_custom_feature()
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Documents Page

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          
      redis:
        image: redis:7
        
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          pip install -r test_requirements.txt
          
      - name: Start services
        run: docker-compose up -d
        
      - name: Wait for services
        run: sleep 10
        
      - name: Run tests
        run: python test_documents_page.py
```

## Performance Considerations

- Tests are designed to run sequentially
- Each test is isolated (can be run individually)
- Detail panel tests require previous tests to pass
- PDF upload is the slowest test (network dependent)

## Notes

- Tests use explicit waits to handle async operations
- XPath selectors are used for flexibility
- Test timeouts: 10 seconds per element
- File upload uses absolute paths for cross-platform compatibility
