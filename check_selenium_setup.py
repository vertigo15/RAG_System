"""
Check Selenium setup and browser availability
"""

import subprocess
import sys
from pathlib import Path

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🔍 Checking Chrome installation...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            print(f"✅ Chrome found at: {path}")
            return True
    
    print("❌ Chrome not found")
    return False


def check_selenium():
    """Check if Selenium is installed"""
    print("\n🔍 Checking Selenium installation...")
    try:
        import selenium
        print(f"✅ Selenium {selenium.__version__} installed")
        return True
    except ImportError:
        print("❌ Selenium not installed")
        return False


def check_webdriver_manager():
    """Check if webdriver-manager is installed"""
    print("\n🔍 Checking webdriver-manager...")
    try:
        import webdriver_manager
        print(f"✅ webdriver-manager installed")
        return True
    except ImportError:
        print("❌ webdriver-manager not installed")
        return False


def test_simple_selenium():
    """Try a simple Selenium test"""
    print("\n🔍 Testing Selenium with Chrome...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        print("   Attempting to create Chrome driver...")
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome driver created successfully!")
        
        print("   Testing navigation...")
        driver.get("https://www.google.com")
        print(f"   Page title: {driver.title}")
        
        driver.quit()
        print("✅ Selenium test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {str(e)}")
        return False


def check_downloads_folder():
    """Check Downloads folder for PDF files"""
    print("\n🔍 Checking Downloads folder...")
    downloads = Path.home() / "Downloads"
    
    if not downloads.exists():
        print(f"❌ Downloads folder not found: {downloads}")
        return False
    
    print(f"✅ Downloads folder found: {downloads}")
    
    pdf_files = list(downloads.glob("*.pdf"))
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files[:5]:  # Show first 5
            print(f"   - {pdf.name} ({pdf.stat().st_size / 1024:.2f} KB)")
    else:
        print("⚠️  No PDF files found in Downloads")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Selenium Setup Diagnostics")
    print("=" * 60)
    
    results = []
    results.append(("Chrome", check_chrome()))
    results.append(("Selenium", check_selenium()))
    results.append(("webdriver-manager", check_webdriver_manager()))
    results.append(("Downloads folder", check_downloads_folder()))
    results.append(("Selenium test", test_simple_selenium()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r for _, r in results)
    if all_passed:
        print("\n✅ All checks passed! Ready to run PDF upload test.")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
