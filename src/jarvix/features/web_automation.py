"""
JARVIX Web Automation Module
Advanced browser automation using Playwright for web interactions.
Uses SYNC API to avoid event loop conflicts with Telegram's async runtime.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Playwright import with fallback - using SYNC API
try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Run: pip install playwright && playwright install chromium")


class WebAutomation:
    """
    Playwright-based browser automation for JARVIX.
    Uses SYNC API to work properly with Telegram's async event loop.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.screenshot_dir = Path(os.environ.get('TEMP', '.')) / 'jarvix_screenshots'
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def start_browser(self, headless: bool = False) -> bool:
        """Launch browser instance."""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        if self.is_running and self.page:
            try:
                # Test if connection is still alive
                self.page.title()
                return True
            except:
                # Connection dead, restart
                self.is_running = False
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self.page = self.context.new_page()
            self.is_running = True
            print("✅ Browser started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            self.is_running = False
            return False
    
    def switch_to_tab(self, index: int) -> bool:
        """Switch to an existing browser tab (by index)."""
        if not self.context:
            return False
        
        try:
            pages = self.context.pages
            if not pages:
                return False
            
            # Clamp index into range
            if index < 0:
                index = 0
            if index >= len(pages):
                return False
            
            self.page = pages[index]
            try:
                # Bring the tab to front for visibility
                self.page.bring_to_front()
            except Exception:
                # Not critical if bring_to_front fails
                pass
            return True
        except Exception as e:
            print(f"⚠️ Failed to switch tab: {e}")
            return False
    
    def stop_browser(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            self.is_running = False
            print("🛑 Browser stopped")
    
    def ensure_browser(self, headless: bool = False) -> bool:
        """Ensure browser is running, start if needed."""
        if not self.is_running or not self.page:
            return self.start_browser(headless)
        
        # Verify connection is alive
        try:
            self.page.title()
            return True
        except:
            self.is_running = False
            return self.start_browser(headless)
    
    def navigate(self, url: str, wait_for: str = 'domcontentloaded') -> bool:
        """Navigate to URL."""
        if not self.ensure_browser():
            return False
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.page.goto(url, wait_until=wait_for, timeout=30000)
            print(f"✅ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def screenshot(self, filename: str = None) -> Optional[str]:
        """Take screenshot of current page."""
        if not self.page:
            return None
        
        try:
            if not filename:
                filename = f"browser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.screenshot_dir / filename
            self.page.screenshot(path=str(filepath), full_page=False)
            print(f"📸 Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def get_page_title(self) -> str:
        """Get current page title."""
        if self.page:
            try:
                return self.page.title()
            except:
                return ""
        return ""
    
    def get_page_text(self) -> str:
        """Extract visible text content from page."""
        if not self.page:
            return ""
        
        try:
            text = self.page.evaluate('''() => {
                const main = document.querySelector('main, article, [role="main"], .content, #content');
                if (main) return main.innerText;
                
                const body = document.body.cloneNode(true);
                const scripts = body.querySelectorAll('script, style, nav, header, footer, aside');
                scripts.forEach(el => el.remove());
                return body.innerText;
            }''')
            return text[:5000]
        except Exception as e:
            print(f"⚠️ Error extracting text: {e}")
            return ""
    
    # ==================== WEB SEARCH ====================
    
    def web_search(self, query: str) -> Dict[str, Any]:
        """Perform Google search and extract results."""
        if not self.ensure_browser():
            return {"error": "Browser not available", "results": []}
        
        try:
            self.page.goto('https://www.google.com', wait_until='domcontentloaded')
            
            # Accept cookies if prompted
            try:
                accept_btn = self.page.locator('button:has-text("Accept all")')
                if accept_btn.count() > 0:
                    accept_btn.click()
                    self.page.wait_for_timeout(500)
            except:
                pass
            
            # Type search query
            search_input = self.page.locator('textarea[name="q"], input[name="q"]')
            search_input.fill(query)
            search_input.press('Enter')
            
            # Wait for results
            self.page.wait_for_selector('#search', timeout=10000)
            self.page.wait_for_timeout(1000)
            
            # Extract search results
            results = self.page.evaluate('''() => {
                const items = [];
                const resultDivs = document.querySelectorAll('#search .g');
                
                for (let i = 0; i < Math.min(resultDivs.length, 5); i++) {
                    const div = resultDivs[i];
                    const titleEl = div.querySelector('h3');
                    const linkEl = div.querySelector('a');
                    const snippetEl = div.querySelector('.VwiC3b, .IsZvec');
                    
                    if (titleEl && linkEl) {
                        items.push({
                            title: titleEl.innerText,
                            url: linkEl.href,
                            snippet: snippetEl ? snippetEl.innerText : ''
                        });
                    }
                }
                return items;
            }''')
            
            # Take screenshot
            safe_query = "".join(c if c.isalnum() or c == ' ' else '_' for c in query[:20])
            screenshot_path = self.screenshot(f"search_{safe_query.replace(' ', '_')}.png")
            
            return {
                "query": query,
                "results": results,
                "screenshot": screenshot_path,
                "count": len(results)
            }
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {"error": str(e), "results": []}
    
    # ==================== PAGE READING ====================
    
    def read_page(self, url: str) -> Dict[str, Any]:
        """Navigate to URL and extract content."""
        if not self.navigate(url):
            return {"error": "Navigation failed"}
        
        try:
            self.page.wait_for_timeout(2000)
            
            title = self.get_page_title()
            text = self.get_page_text()
            screenshot_path = self.screenshot()
            
            return {
                "url": url,
                "title": title,
                "content": text,
                "screenshot": screenshot_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== FORM FILLING ====================
    
    def fill_form(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Fill form fields on current page."""
        if not self.page:
            return {"error": "No page open"}
        
        filled = []
        failed = []
        
        try:
            for field_name, value in form_data.items():
                selectors = [
                    f'input[name="{field_name}"]',
                    f'input[id="{field_name}"]',
                    f'input[placeholder*="{field_name}" i]',
                    f'textarea[name="{field_name}"]',
                ]
                
                field_filled = False
                for selector in selectors:
                    try:
                        locator = self.page.locator(selector).first
                        if locator.count() > 0:
                            locator.fill(value)
                            filled.append(field_name)
                            field_filled = True
                            break
                    except:
                        continue
                
                if not field_filled:
                    failed.append(field_name)
            
            screenshot_path = self.screenshot("form_filled.png")
            
            return {
                "filled": filled,
                "failed": failed,
                "screenshot": screenshot_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== E-COMMERCE ====================
    
    def amazon_add_to_cart(self, product_query: str) -> Dict[str, Any]:
        """Search Amazon and add first result to cart."""
        if not self.ensure_browser():
            return {"error": "Browser not available"}
        
        try:
            self.page.goto('https://www.amazon.in', wait_until='domcontentloaded')
            self.page.wait_for_timeout(2000)
            
            # Search for product
            search_box = self.page.locator('#twotabsearchtextbox')
            search_box.fill(product_query)
            search_box.press('Enter')
            
            # Wait for results
            self.page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
            self.page.wait_for_timeout(1500)
            
            # Click first product
            first_product = self.page.locator('[data-component-type="s-search-result"]').first
            first_product.locator('h2 a').first.click()
            
            # Wait for product page
            self.page.wait_for_selector('#productTitle', timeout=10000)
            self.page.wait_for_timeout(1500)
            
            # Get product info
            title = self.page.locator('#productTitle').text_content()
            title = title.strip() if title else product_query
            
            # Try to get price
            price = ""
            try:
                price_elem = self.page.locator('.a-price-whole').first
                if price_elem.count() > 0:
                    price = price_elem.text_content()
            except:
                pass
            
            # Take screenshot before adding
            self.screenshot("product_page.png")
            
            # Click Add to Cart
            add_btn = self.page.locator('#add-to-cart-button')
            if add_btn.count() > 0:
                add_btn.click()
                self.page.wait_for_timeout(2000)
                screenshot_path = self.screenshot("added_to_cart.png")
                
                return {
                    "success": True,
                    "product": title,
                    "price": price,
                    "screenshot": screenshot_path
                }
            else:
                return {
                    "success": False,
                    "error": "Add to Cart button not found",
                    "product": title
                }
                
        except Exception as e:
            print(f"❌ Amazon add to cart failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
web_automation = WebAutomation()


# ==================== SIMPLE WRAPPERS ====================
# Direct function calls - no async/event loop issues

def run_web_search(query: str) -> Dict[str, Any]:
    """Run web search."""
    return web_automation.web_search(query)


def run_read_page(url: str) -> Dict[str, Any]:
    """Read a webpage."""
    return web_automation.read_page(url)


def run_fill_form(form_data: Dict[str, str]) -> Dict[str, Any]:
    """Fill form on current page."""
    return web_automation.fill_form(form_data)


def run_amazon_add_to_cart(product: str) -> Dict[str, Any]:
    """Add product to Amazon cart."""
    return web_automation.amazon_add_to_cart(product)


def run_browser_screenshot() -> Optional[str]:
    """Take browser screenshot."""
    return web_automation.screenshot()


def stop_browser():
    """Stop the browser."""
    web_automation.stop_browser()
