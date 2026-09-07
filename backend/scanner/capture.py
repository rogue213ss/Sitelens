import asyncio
import logging
from typing import Any

from playwright.async_api import async_playwright, Page, Request, Response

from scanner.security import security_route_handler

logger = logging.getLogger(__name__)

async def capture_evidence(url: str) -> dict[str, Any]:
    """
    Run the headless browser scan, returning structured evidence.
    """
    evidence = {
        "page": {},
        "links": [],
        "scripts": [],
        "stylesheets": [],
        "images": [],
        "network_requests": [],
        "performance": {},
        "screenshot": None,
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create an isolated context
        context = await browser.new_context(
            user_agent="SiteLens/1.0",
            ignore_https_errors=True
        )
        
        page = await context.new_page()

        # Route ALL requests through the SSRF protection
        await page.route("**/*", security_route_handler)

        # Collect network requests
        async def on_response(response: Response):
            request = response.request
            evidence["network_requests"].append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
            })

        page.on("response", on_response)

        try:
            # Navigate to the page
            response = await page.goto(url, timeout=30000, wait_until="networkidle")
            
            if not response:
                raise Exception("No response received from the page.")
            
            # Page evidence
            evidence["page"] = {
                "requested_url": url,
                "final_url": page.url,
                "page_title": await page.title(),
                "status_code": response.status,
                "content_type": response.headers.get("content-type"),
                "viewport": str(page.viewport_size),
                "user_agent": await page.evaluate("navigator.userAgent"),
                "html": await page.content(),
            }

            # Scripts
            scripts = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('script')).map(s => ({
                    url: s.src || null,
                    is_inline: !s.src,
                    type: s.type || null
                }));
            }''')
            evidence["scripts"] = scripts

            # Stylesheets
            stylesheets = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('link[rel="stylesheet"], style')).map(s => ({
                    url: s.href || null,
                    is_inline: s.tagName.toLowerCase() === 'style'
                }));
            }''')
            evidence["stylesheets"] = stylesheets

            # Images
            images = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('img')).map(img => ({
                    url: img.src || null,
                    alt_text: img.alt || null,
                    width: img.naturalWidth || null,
                    height: img.naturalHeight || null
                })).filter(i => i.url);
            }''')
            evidence["images"] = images

            # Links
            links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    url: a.href || null,
                    text: a.innerText || null,
                    is_external: a.host !== window.location.host
                })).filter(l => l.url);
            }''')
            evidence["links"] = links

            # Performance
            perf = await page.evaluate('''() => {
                if (window.performance && window.performance.timing) {
                    const t = window.performance.timing;
                    return {
                        navigation_start: t.navigationStart,
                        dom_content_loaded: t.domContentLoadedEventEnd - t.navigationStart,
                        load_event: t.loadEventEnd - t.navigationStart,
                    };
                }
                return {};
            }''')
            perf["request_count"] = len(evidence["network_requests"])
            evidence["performance"] = perf

            # Screenshot
            screenshot_bytes = await page.screenshot(full_page=True, timeout=10000)
            evidence["screenshot"] = screenshot_bytes

        except Exception as e:
            logger.error(f"Error during capture: {e}")
            raise e
        finally:
            await context.close()
            await browser.close()

    return evidence
