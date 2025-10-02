"""
Test script to diagnose Playwright browser issues
Run this to check if Playwright is working properly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

async def test_playwright():
    """Test Playwright browser launching"""
    print("Testing Playwright browser setup...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            print("\n1. Testing Firefox...")
            try:
                browser = await p.firefox.launch(headless=False)
                page = await browser.new_page()
                await page.goto("https://www.google.com")
                print("[OK] Firefox works!")
                await browser.close()
            except Exception as e:
                print(f"[FAIL] Firefox failed: {e}")
                
                print("\n2. Testing Chrome...")
                try:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    await page.goto("https://www.google.com")
                    print("[OK] Chrome works!")
                    await browser.close()
                except Exception as e:
                    print(f"[FAIL] Chrome failed: {e}")
                    
                    print("\n3. Testing Edge...")
                    try:
                        browser = await p.chromium.launch(
                            headless=False,
                            channel="msedge"
                        )
                        page = await browser.new_page()
                        await page.goto("https://www.google.com")
                        print("[OK] Edge works!")
                        await browser.close()
                    except Exception as e:
                        print(f"[FAIL] Edge failed: {e}")
                        
                        print("\n[ERROR] No browsers are working!")
                        print("\nTroubleshooting steps:")
                        print("1. Run: playwright install")
                        print("2. Run: playwright install firefox")
                        print("3. Run: playwright install chromium")
                        print("4. Check if antivirus is blocking browser launch")
                        print("5. Try running as administrator")
                        return False
            
            print("\n[SUCCESS] Playwright is working correctly!")
            return True
            
    except ImportError as e:
        print(f"[ERROR] Playwright not installed: {e}")
        print("Install with: pip install playwright")
        print("Then run: playwright install")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PLAYWRIGHT BROWSER TEST")
    print("=" * 50)
    
    result = asyncio.run(test_playwright())
    
    if result:
        print("\n[SUCCESS] All tests passed! Playwright should work in the desktop app.")
    else:
        print("\n[FAILED] Tests failed! Please fix the issues above before using the desktop app.")
    
    input("\nPress Enter to exit...")
