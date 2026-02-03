"""
Debug script to inspect the DOM structure of the Documents page
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    # Navigate to page
    url = "http://localhost:3100/documents"
    print(f"🌐 Navigating to {url}...")
    driver.get(url)
    time.sleep(3)
    
    # Print page title and URL
    print(f"\n📄 Page Title: {driver.title}")
    print(f"📍 Current URL: {driver.current_url}")
    
    # Get page source
    page_source = driver.page_source
    print(f"\n📊 Page Source Length: {len(page_source)} bytes")
    
    # Check for key elements
    print("\n🔍 Searching for key elements:")
    
    # H1 elements
    h1_elements = driver.find_elements(By.TAG_NAME, "h1")
    print(f"\n  <h1> elements found: {len(h1_elements)}")
    for i, h1 in enumerate(h1_elements):
        print(f"    [{i}] {h1.text}")
    
    # Button elements
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n  <button> elements found: {len(buttons)}")
    for i, btn in enumerate(buttons[:10]):  # Show first 10
        print(f"    [{i}] {btn.text}")
    
    # Input elements
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n  <input> elements found: {len(inputs)}")
    for i, inp in enumerate(inputs):
        placeholder = inp.get_attribute("placeholder") or "no placeholder"
        print(f"    [{i}] type={inp.get_attribute('type')} placeholder='{placeholder}'")
    
    # Select elements
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n  <select> elements found: {len(selects)}")
    
    # Table elements
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"\n  <table> elements found: {len(tables)}")
    
    # Check for specific text
    print("\n🔎 Text search:")
    if "Documents" in page_source:
        print("  ✅ 'Documents' found in page source")
    if "Upload" in page_source:
        print("  ✅ 'Upload' found in page source")
    if "Refresh" in page_source:
        print("  ✅ 'Refresh' found in page source")
    if "Search" in page_source:
        print("  ✅ 'Search' found in page source")
    
    # Check for error messages
    print("\n⚠️ Checking for errors:")
    if "error" in page_source.lower():
        print("  ⚠️ 'error' found in page")
    if "Cannot GET" in page_source:
        print("  ⚠️ 'Cannot GET' found in page")
    if "404" in page_source:
        print("  ⚠️ '404' found in page")
    
    # Print body content preview
    print("\n📋 Page body preview (first 500 chars):")
    body = driver.find_element(By.TAG_NAME, "body")
    print(f"  {body.text[:500]}")
    
finally:
    driver.quit()
    print("\n✅ Done")
