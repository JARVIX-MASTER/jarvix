"""
JARVIX Web Automation Module
Advanced browser automation using Playwright for web interactions.
"""

import asyncio
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Playwright import with fallback
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Run: pip install playwright && playwright install chromium")


class WebAutomation:
    """
    Playwright-based browser automation for JARVIX.
    Supports web search, page reading, form filling, and e-commerce actions.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.screenshot_dir = Path(os.environ.get('TEMP', '.')) / 'jarvix_screenshots'
        self.screenshot_dir.mkdir(exist_ok=True)
    
    async def start_browser(self, headless: bool = False) -> bool:
        """
        Launch browser instance.
        Args:
            headless: If True, browser runs invisibly
        """
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        if self.is_running:
            return True
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            self.is_running = True
            print("✅ Browser started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            return False
    
    async def stop_browser(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            self.is_running = False
            print("🛑 Browser stopped")
    
    async def ensure_browser(self, headless: bool = False) -> bool:
        """Ensure browser is running, start if needed."""
        if not self.is_running:
            return await self.start_browser(headless)
        return True
    
    async def navigate(self, url: str, wait_for: str = 'domcontentloaded') -> bool:
        """
        Navigate to URL.
        Args:
            url: Target URL
            wait_for: Wait condition ('load', 'domcontentloaded', 'networkidle')
        """
        if not await self.ensure_browser():
            return False
        
        try:
            # Add https if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            await self.page.goto(url, wait_until=wait_for, timeout=30000)
            print(f"✅ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    async def screenshot(self, filename: str = None) -> Optional[str]:
        """
        Take screenshot of current page.
        Returns: Path to screenshot file
        """
        if not self.page:
            return None
        
        try:
            if not filename:
                filename = f"browser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.screenshot_dir / filename
            await self.page.screenshot(path=str(filepath), full_page=False)
            print(f"📸 Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    async def get_page_title(self) -> str:
        """Get current page title."""
        if self.page:
            return await self.page.title()
        return ""
    
    async def get_page_text(self) -> str:
        """Extract visible text content from page."""
        if not self.page:
            return ""
        
        try:
            # Extract main content text
            text = await self.page.evaluate('''() => {
                // Try to find main content area
                const main = document.querySelector('main, article, [role="main"], .content, #content');
                if (main) return main.innerText;
                
                // Fallback to body, but remove scripts/styles
                const body = document.body.cloneNode(true);
                const scripts = body.querySelectorAll('script, style, nav, header, footer, aside');
                scripts.forEach(el => el.remove());
                return body.innerText;
            }''')
            return text[:5000]  # Limit to 5000 chars
        except Exception as e:
            print(f"⚠️ Error extracting text: {e}")
            return ""
    
    # ==================== WEB SEARCH ====================
    
    async def web_search(self, query: str) -> Dict[str, Any]:
        """
        Perform Google search and extract results.
        Args:
            query: Search query
        Returns:
            Dict with results list and screenshot path
        """
        if not await self.ensure_browser():
            return {"error": "Browser not available", "results": []}
        
        try:
            # Navigate to Google
            await self.page.goto('https://www.google.com', wait_until='domcontentloaded')
            
            # Accept cookies if prompted (region-dependent)
            try:
                accept_btn = self.page.locator('button:has-text("Accept all")')
                if await accept_btn.count() > 0:
                    await accept_btn.click()
                    await self.page.wait_for_timeout(500)
            except:
                pass
            
            # Type search query
            search_input = self.page.locator('textarea[name="q"], input[name="q"]')
            await search_input.fill(query)
            await search_input.press('Enter')
            
            # Wait for results
            await self.page.wait_for_selector('#search', timeout=10000)
            await self.page.wait_for_timeout(1000)  # Let results fully load
            
            # Extract search results
            results = await self.page.evaluate('''() => {
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
            screenshot_path = await self.screenshot(f"search_{query[:20].replace(' ', '_')}.png")
            
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
    
    async def read_page(self, url: str) -> Dict[str, Any]:
        """
        Navigate to URL and extract content.
        Args:
            url: Page URL to read
        Returns:
            Dict with title, text content, and screenshot
        """
        if not await self.navigate(url):
            return {"error": "Navigation failed"}
        
        try:
            await self.page.wait_for_timeout(2000)  # Let page load
            
            title = await self.get_page_title()
            text = await self.get_page_text()
            screenshot_path = await self.screenshot()
            
            return {
                "url": url,
                "title": title,
                "content": text,
                "screenshot": screenshot_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== FORM FILLING ====================
    
    async def fill_form(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Fill form fields on current page.
        Args:
            form_data: Dict mapping field identifiers to values
                       e.g., {"email": "user@email.com", "name": "John"}
        Returns:
            Dict with filled fields and screenshot
        """
        if not self.page:
            return {"error": "No page open"}
        
        filled = []
        failed = []
        
        try:
            for field_name, value in form_data.items():
                # Try multiple selector strategies
                selectors = [
                    f'input[name="{field_name}"]',
                    f'input[id="{field_name}"]',
                    f'input[placeholder*="{field_name}" i]',
                    f'textarea[name="{field_name}"]',
                    f'input[type="text"]:near(:text("{field_name}"))',
                ]
                
                field_filled = False
                for selector in selectors:
                    try:
                        locator = self.page.locator(selector).first
                        if await locator.count() > 0:
                            await locator.fill(value)
                            filled.append(field_name)
                            field_filled = True
                            break
                    except:
                        continue
                
                if not field_filled:
                    failed.append(field_name)
            
            screenshot_path = await self.screenshot("form_filled.png")
            
            return {
                "filled": filled,
                "failed": failed,
                "screenshot": screenshot_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== E-COMMERCE ====================
    
    async def amazon_add_to_cart(self, product_query: str) -> Dict[str, Any]:
        """
        Search Amazon and add first result to cart.
        Args:
            product_query: Product to search for
        Returns:
            Dict with product info and screenshot
        """
        if not await self.ensure_browser():
            return {"error": "Browser not available"}
        
        try:
            # Navigate to Amazon India
            await self.page.goto('https://www.amazon.in', wait_until='domcontentloaded')
            await self.page.wait_for_timeout(2000)
            
            # Search for product
            search_box = self.page.locator('#twotabsearchtextbox')
            await search_box.fill(product_query)
            await search_box.press('Enter')
            
            # Wait for results
            await self.page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
            await self.page.wait_for_timeout(1500)
            
            # Click first product
            first_product = self.page.locator('[data-component-type="s-search-result"]').first
            product_title = await first_product.locator('h2 a span').first.text_content()
            await first_product.locator('h2 a').first.click()
            
            # Wait for product page
            await self.page.wait_for_selector('#productTitle', timeout=10000)
            await self.page.wait_for_timeout(1500)
            
            # Get product info
            title = await self.page.locator('#productTitle').text_content()
            title = title.strip() if title else product_query
            
            # Try to get price
            price = ""
            try:
                price_elem = self.page.locator('.a-price-whole').first
                if await price_elem.count() > 0:
                    price = await price_elem.text_content()
            except:
                pass
            
            # Take screenshot before adding
            await self.screenshot("product_page.png")
            
            # Click Add to Cart
            add_btn = self.page.locator('#add-to-cart-button')
            if await add_btn.count() > 0:
                await add_btn.click()
                await self.page.wait_for_timeout(2000)
                screenshot_path = await self.screenshot("added_to_cart.png")
                
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
    
    # ==================== UTILITY METHODS ====================
    
    async def click_element(self, selector_or_text: str) -> bool:
        """Click an element by selector or visible text."""
        if not self.page:
            return False
        
        try:
            # Try as selector first
            locator = self.page.locator(selector_or_text)
            if await locator.count() > 0:
                await locator.first.click()
                return True
            
            # Try as text
            locator = self.page.get_by_text(selector_or_text, exact=False)
            if await locator.count() > 0:
                await locator.first.click()
                return True
            
            return False
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    async def type_text(self, selector: str, text: str) -> bool:
        """Type text into an input field."""
        if not self.page:
            return False
        
        try:
            await self.page.locator(selector).first.fill(text)
            return True
        except Exception as e:
            print(f"❌ Type failed: {e}")
            return False


# Singleton instance
web_automation = WebAutomation()


# ==================== SYNC WRAPPERS ====================
# These allow calling async methods from sync context

def run_web_search(query: str) -> Dict[str, Any]:
    """Sync wrapper for web search."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(web_automation.web_search(query))
        return result
    finally:
        loop.close()


def run_read_page(url: str) -> Dict[str, Any]:
    """Sync wrapper for page reading."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(web_automation.read_page(url))
        return result
    finally:
        loop.close()


def run_fill_form(form_data: Dict[str, str]) -> Dict[str, Any]:
    """Sync wrapper for form filling."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(web_automation.fill_form(form_data))
        return result
    finally:
        loop.close()


def run_amazon_add_to_cart(product: str) -> Dict[str, Any]:
    """Sync wrapper for Amazon add to cart."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(web_automation.amazon_add_to_cart(product))
        return result
    finally:
        loop.close()


def run_browser_screenshot() -> Optional[str]:
    """Sync wrapper for taking screenshot."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(web_automation.screenshot())
        return result
    finally:
        loop.close()


def stop_browser():
    """Sync wrapper to stop browser."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(web_automation.stop_browser())
    finally:
        loop.close()
