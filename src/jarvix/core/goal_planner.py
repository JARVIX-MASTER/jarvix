"""
JARVIX Goal Planner - LLM-Powered Task Decomposition
Converts natural language goals into structured action plans.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ActionStep:
    """Single action step in a plan."""
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ActionPlan:
    """Complete action plan for a goal."""
    goal: str
    steps: List[ActionStep] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    # Optional rough estimate of how many seconds this plan will take.
    # Not all plans need to set this explicitly.
    estimated_time: int = 0


# Site-specific search selectors and shopping profiles
SITE_SEARCH_CONFIG = {
    "youtube.com": {
        "search_selector": "input#search, input[name='search_query']",
        "submit_selector": None,  # Press Enter instead of clicking
        "results_selector": "ytd-video-renderer, ytd-rich-item-renderer"
    },
    "amazon.in": {
        "search_selector": "#twotabsearchtextbox",
        "submit_selector": "#nav-search-submit-button",
        "results_selector": "[data-component-type='s-search-result']",
        # Shopping helpers
        "product_link_selector": "[data-component-type='s-search-result'] h2 a, .s-result-item h2 a",
        "product_price_selector": ".a-price .a-offscreen, .a-price-whole, #priceblock_ourprice, #priceblock_dealprice",
        "product_title_selector": "#productTitle, .product-title",
        "product_rating_selector": ".a-icon-alt"
    },
    "amazon.com": {
        "search_selector": "#twotabsearchtextbox",
        "submit_selector": "#nav-search-submit-button",
        "results_selector": "[data-component-type='s-search-result']",
        # Shopping helpers
        "product_link_selector": "[data-component-type='s-search-result'] h2 a, .s-result-item h2 a",
        "product_price_selector": ".a-price .a-offscreen, .a-price-whole, #priceblock_ourprice, #priceblock_dealprice",
        "product_title_selector": "#productTitle, .product-title",
        "product_rating_selector": ".a-icon-alt"
    },
    "google.com": {
        "search_selector": "textarea[name='q'], input[name='q']",
        "submit_selector": None,  # Press Enter
        "results_selector": "#search .g"
    },
    "flipkart.com": {
        "search_selector": "input[name='q'], input._3704LK",
        "submit_selector": "button[type='submit'], button._2iLD__",
        "results_selector": "div._1AtVbE, div._4ddWXP",
        # Shopping helpers
        "product_link_selector": "div._1AtVbE a, div._4ddWXP a",
        "product_price_selector": "div._30jeq3",
        "product_title_selector": "span.B_NuCI",
        "product_rating_selector": "div._3LWZlK"
    },
    "github.com": {
        "search_selector": "input[name='q']",
        "submit_selector": None,
        "results_selector": ".repo-list-item, .Box-row"
    },
    "ebay.com": {
        "search_selector": "input[aria-label*='Search' i], input[type='text'][name='_nkw']",
        "submit_selector": "input[type='submit'][value*='Search' i], button[aria-label*='Search' i]",
        "results_selector": "li.s-item",
        # Shopping helpers
        "product_link_selector": "li.s-item a.s-item__link",
        "product_price_selector": ".s-item__price",
        "product_title_selector": "#itemTitle, .s-item__title",
        "product_rating_selector": ".b-starrating__star, .x-star-rating span.clipped"
    }
}


# Common site aliases for pattern matching and multi-site flows
SITE_ALIASES = {
    "youtube": "youtube.com",
    "amazon": "amazon.in",
    "amazon india": "amazon.in",
    "amazon us": "amazon.com",
    "flipkart": "flipkart.com",
    "google": "google.com",
    "github": "github.com",
    "ebay": "ebay.com",
}


PLANNER_SYSTEM_PROMPT = """You are a browser automation planner for JARVIX AI assistant.

Given a user goal, output a JSON action plan with sequential steps.

AVAILABLE ACTIONS:
- navigate: {"action": "navigate", "url": "https://..."}
- click: {"action": "click", "selector": "CSS selector", "text": "optional visible text"}
- type: {"action": "type", "selector": "CSS selector", "text": "text to type"}
- press_key: {"action": "press_key", "key": "Enter/Tab/Escape"}
- scroll: {"action": "scroll", "direction": "down/up", "amount": 500}
- wait_for: {"action": "wait_for", "selector": "CSS selector", "timeout": 5000}
- extract: {"action": "extract", "selector": "CSS selector", "attribute": "text/href/src", "save_as": "variable_name"}
- screenshot: {"action": "screenshot", "name": "description"}
- wait: {"action": "wait", "ms": 1000}

RULES:
1. Always start with navigation if a URL is mentioned
2. Use wait_for after navigation before interacting
3. Use specific CSS selectors when possible
4. Add screenshot at important checkpoints
5. For site searches, use the site's search box, not Google

OUTPUT FORMAT (JSON only, no markdown):
{
  "goal": "description",
  "steps": [
    {"action": "...", ...},
    ...
  ]
}"""


class GoalPlanner:
    """Plans browser actions from natural language goals."""
    
    def __init__(self):
        self.site_config = SITE_SEARCH_CONFIG
    
    def plan(self, goal: str) -> ActionPlan:
        """
        Convert a goal into an action plan.
        Uses pattern matching first, falls back to LLM for complex goals.
        """
        goal_lower = goal.lower().strip()
        
        # Try pattern-based planning first (fast)
        plan = self._pattern_plan(goal_lower, goal)
        if plan and plan.steps:
            return plan
        
        # Fall back to LLM planning (slower but handles complex goals)
        return self._llm_plan(goal)
    
    def _pattern_plan(self, goal_lower: str, original_goal: str) -> Optional[ActionPlan]:
        """Pattern-based planning for common goals."""
        # Use shared site aliases
        site_aliases = SITE_ALIASES
        
        # Pattern: "open youtube and search pikachu" (short site name)
        short_match = re.search(
            r'(?:open|go to|visit|browse)\s+(youtube|amazon|flipkart|google|github|ebay)\s+(?:and|then)\s+(?:search|find|look for)\s+(.+)',
            goal_lower
        )
        if short_match:
            site = site_aliases.get(short_match.group(1), short_match.group(1) + ".com")
            query = short_match.group(2).strip()
            return self._create_site_search_plan(site, query)
        
        # Pattern: "open X.com and search Y" (full domain)
        compound_match = re.search(
            r'(?:open|go to|visit|browse)\s+(\S+\.(?:com|in|org|net|io))\s+(?:and|then)\s+(?:search|find|look for)\s+(.+)',
            goal_lower
        )
        if compound_match:
            site = compound_match.group(1)
            query = compound_match.group(2).strip()
            return self._create_site_search_plan(site, query)
        
        # Pattern: "search X on Y" or "find X on Y"
        site_search_match = re.search(
            r'(?:search|find|look for)\s+(.+?)\s+(?:on|in)\s+(\S+\.(?:com|in|org|net|io))',
            goal_lower
        )
        if site_search_match:
            query = site_search_match.group(1).strip()
            site = site_search_match.group(2)
            return self._create_site_search_plan(site, query)
        
        # Pattern: "youtube search X" or "amazon search X"
        quick_search_match = re.search(
            r'(youtube|amazon|flipkart|google|github)\s+(?:search|find)\s+(.+)',
            goal_lower
        )
        if quick_search_match:
            site = site_aliases.get(quick_search_match.group(1), quick_search_match.group(1) + ".com")
            query = quick_search_match.group(2).strip()
            return self._create_site_search_plan(site, query)
        
        # Pattern: "find price of X on amazon"
        price_match = re.search(
            r'(?:find|get|check)\s+(?:the\s+)?price\s+(?:of\s+)?(.+?)\s+(?:on|from)\s+(amazon|flipkart)',
            goal_lower
        )
        if price_match:
            product = price_match.group(1).strip()
            site = price_match.group(2) + (".in" if "amazon" in price_match.group(2) else ".com")
            return self._create_price_check_plan(site, product)
        
        # Pattern: "compare prices for X across amazon, flipkart and ebay"
        multi_compare_match = re.search(
            r'compare\s+prices?\s+(?:for|of)\s+(.+?)(?:\s+(?:across|on|between)\s+(.+))?$',
            goal_lower
        )
        if multi_compare_match:
            product = multi_compare_match.group(1).strip()
            sites_raw = (multi_compare_match.group(2) or "").strip()
            
            sites: List[str] = []
            if sites_raw:
                # Normalize separators: "amazon, flipkart and ebay" -> "amazon, flipkart, ebay"
                sites_clean = sites_raw.replace(" and ", ",")
                for part in sites_clean.split(","):
                    name = part.strip()
                    if not name:
                        continue
                    # Map via aliases, or keep as-is
                    mapped = SITE_ALIASES.get(name, SITE_ALIASES.get(name.replace(".com", ""), name))
                    sites.append(mapped)
            
            # Default sites if none explicitly mentioned
            if not sites:
                sites = ["amazon.in", "flipkart.com", "ebay.com"]
            
            return self._create_multi_site_compare_plan(product, sites)
        
        # Pattern: Simple "open youtube" or "open amazon.com"
        simple_open_match = re.search(
            r'(?:open|go\s+to|visit|browse)\s+(\S+)',
            goal_lower
        )
        if simple_open_match:
            target = simple_open_match.group(1).strip()
            # Map short names to full URLs
            if target in site_aliases:
                target = site_aliases[target]
            elif not any(x in target for x in ['.com', '.in', '.org', '.net', '.io', 'http']):
                target = target + ".com"
            
            return self._create_simple_navigate_plan(target)
        
        return None
    
    def _create_simple_navigate_plan(self, url: str) -> ActionPlan:
        """Create a simple navigation plan (just open a site)."""
        if not url.startswith("http"):
            url = "https://" + url
        
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        
        return ActionPlan(
            goal=f"Open {domain}",
            steps=[
                ActionStep(
                    action="navigate",
                    params={"url": url},
                    description=f"Open {domain}"
                ),
                ActionStep(
                    action="wait",
                    params={"ms": 500},
                    description="Wait for page to load"
                ),
                ActionStep(
                    action="screenshot",
                    params={"name": f"page_{domain.replace('.', '_')}"},
                    description="Capture page"
                )
            ],
            estimated_time=3
        )
    
    def _create_site_search_plan(self, site: str, query: str) -> ActionPlan:
        """Create a plan to search within a specific site."""
        # Ensure site has protocol
        if not site.startswith("http"):
            site = "https://www." + site if not site.startswith("www.") else "https://" + site
        
        # Get site config
        domain = site.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        config = self.site_config.get(domain, {})
        
        steps = [
            ActionStep(
                action="navigate",
                params={"url": site},
                description=f"Open {domain}"
            ),
            ActionStep(
                action="wait",
                params={"ms": 500},
                description="Wait for page to load"
            ),
        ]
        
        # Add search steps
        search_selector = config.get("search_selector", "input[type='search'], input[name='q'], input[name='search']")
        steps.append(ActionStep(
            action="wait_for",
            params={"selector": search_selector, "timeout": 10000},
            description="Wait for search box"
        ))
        
        steps.append(ActionStep(
            action="type",
            params={"selector": search_selector, "text": query},
            description=f"Type search query: {query}"
        ))
        
        # Submit search
        submit_selector = config.get("submit_selector")
        if submit_selector:
            steps.append(ActionStep(
                action="click",
                params={"selector": submit_selector},
                description="Click search button"
            ))
        else:
            steps.append(ActionStep(
                action="press_key",
                params={"key": "Enter"},
                description="Press Enter to search"
            ))
        
        # Wait for results
        results_selector = config.get("results_selector", "main, #content, .results")
        steps.append(ActionStep(
            action="wait_for",
            params={"selector": results_selector, "timeout": 10000},
            description="Wait for search results"
        ))
        
        steps.append(ActionStep(
            action="wait",
            params={"ms": 300},
            description="Let results fully load"
        ))
        
        steps.append(ActionStep(
            action="screenshot",
            params={"name": f"search_{query[:20].replace(' ', '_')}"},
            description="Capture search results"
        ))
        
        return ActionPlan(
            goal=f"Search '{query}' on {domain}",
            steps=steps,
            context={"site": domain, "query": query}
        )
    
    def _create_price_check_plan(self, site: str, product: str, prefix: str = "") -> ActionPlan:
        """Create a plan to find product price on a shopping site.
        
        The optional `prefix` is used for multi-site comparisons so that fields
        like price/product_name don't overwrite each other in extracted_data.
        """
        plan = self._create_site_search_plan(site, product)
        
        # Resolve domain & config
        domain = (
            site.replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
            .split("/")[0]
        )
        config = self.site_config.get(domain, {})
        
        product_link_selector = config.get(
            "product_link_selector",
            "[data-component-type='s-search-result'] h2 a, .s-result-item h2 a",
        )
        price_selector = config.get(
            "product_price_selector",
            ".a-price .a-offscreen, .a-price-whole, #priceblock_ourprice, #priceblock_dealprice",
        )
        title_selector = config.get(
            "product_title_selector",
            "#productTitle, .product-title",
        )
        rating_selector = config.get(
            "product_rating_selector",
            ".a-icon-alt, ._3LWZlK, .x-star-rating span.clipped",
        )

        price_key = f"{prefix}price" if prefix else "price"
        name_key = f"{prefix}product_name" if prefix else "product_name"
        rating_key = f"{prefix}rating" if prefix else "rating"
        
        # Add steps to open first product from search results
        plan.steps.append(ActionStep(
            action="click",
            params={"selector": product_link_selector},
            description="Click first product"
        ))
        
        plan.steps.append(ActionStep(
            action="wait_for",
            params={"selector": price_selector, "timeout": 10000},
            description="Wait for product page"
        ))
        
        # Extract price
        plan.steps.append(ActionStep(
            action="extract",
            params={"selector": price_selector, "attribute": "text", "save_as": price_key},
            description="Extract price"
        ))
        
        # Extract product name
        plan.steps.append(ActionStep(
            action="extract",
            params={"selector": title_selector, "attribute": "text", "save_as": name_key},
            description="Extract product name"
        ))
        
        # Extract rating if available
        plan.steps.append(ActionStep(
            action="extract",
            params={"selector": rating_selector, "attribute": "text", "save_as": rating_key},
            description="Extract rating (if available)"
        ))
        
        plan.steps.append(ActionStep(
            action="screenshot",
            params={"name": "product_price"},
            description="Capture product page"
        ))
        
        plan.goal = f"Find price of '{product}' on {domain}"
        return plan

    def _create_multi_site_compare_plan(self, product: str, sites: List[str]) -> ActionPlan:
        """Create a plan to compare prices for a product across multiple sites."""
        normalized_sites: List[str] = []
        
        for raw in sites:
            if not raw:
                continue
            name = raw.strip().lower()
            if not name:
                continue
            
            # Map via aliases first
            mapped = SITE_ALIASES.get(name) or SITE_ALIASES.get(name.replace(".com", ""), name)
            domain = (
                mapped.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
                .split("/")[0]
            )
            
            # Ensure we keep only domain (no path)
            if not any(tld in domain for tld in [".com", ".in", ".org", ".net", ".io"]):
                # Best-effort default TLD
                domain = domain + ".com"
            
            if domain not in normalized_sites:
                normalized_sites.append(domain)
        
        if not normalized_sites:
            normalized_sites = ["amazon.in", "flipkart.com", "ebay.com"]
        
        all_steps: List[ActionStep] = []
        context_sites: List[str] = []
        
        for domain in normalized_sites:
            url = "https://www." + domain
            prefix = domain.split(".")[0] + "_"
            sub_plan = self._create_price_check_plan(url, product, prefix=prefix)
            all_steps.extend(sub_plan.steps)
            context_sites.append(domain)
        
        return ActionPlan(
            goal=f"Compare prices for '{product}' across {', '.join(context_sites)}",
            steps=all_steps,
            context={
                "type": "multi_site_compare",
                "product": product,
                "sites": context_sites,
            }
        )
    
    def _llm_plan(self, goal: str) -> ActionPlan:
        """Use LLM to create plan for complex goals."""
        # Allow disabling LLM planning entirely via environment.
        use_llm = os.getenv("PLANNER_USE_LLM", "false").lower() in ("1", "true", "yes", "on")
        if not use_llm:
            print("⚠️ LLM planner disabled via PLANNER_USE_LLM. Using fallback plan.")
            return self._fallback_plan(goal)

        model_name = os.getenv("PLANNER_MODEL_NAME", "qwen2.5-coder:7b")

        try:
            import ollama
            
            response = ollama.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Create an action plan for: {goal}"}
                ]
            )
            
            response_text = response['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                plan_data = json.loads(json_match.group())
                
                steps = []
                for step_data in plan_data.get("steps", []):
                    action = step_data.pop("action", "unknown")
                    steps.append(ActionStep(
                        action=action,
                        params=step_data,
                        description=step_data.get("description", "")
                    ))
                
                if steps:
                    return ActionPlan(
                        goal=plan_data.get("goal", goal),
                        steps=steps
                    )
        except Exception as e:
            print(f"⚠️ LLM planning failed: {e}")
        
        # Fallback: simple navigate plan
        return self._fallback_plan(goal)

    def _fallback_plan(self, goal: str) -> ActionPlan:
        """Fallback plan when LLM is disabled or fails.
        
        For now this simply opens Google so the user can search manually.
        """
        return ActionPlan(
            goal=goal,
            steps=[ActionStep(
                action="navigate",
                params={"url": "https://www.google.com"},
                description="Fallback: Open Google"
            )]
        )


# Singleton instance
goal_planner = GoalPlanner()


def plan_goal(goal: str) -> ActionPlan:
    """Public function to plan a goal."""
    return goal_planner.plan(goal)
