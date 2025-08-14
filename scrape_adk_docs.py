#!/usr/bin/env python3
"""
Google ADK Documentation Scraper
Automatically fetches and converts all documentation pages to markdown format
"""

import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import re

class ADKDocScraper:
    def __init__(self, base_url="https://google.github.io/adk-docs/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # All pages discovered from navigation structure
        self.pages = [
            "",  # Home page
            "get-started/",
            "get-started/installation/",
            "get-started/quickstart/",
            "get-started/streaming/",
            "get-started/streaming/quickstart-streaming/",
            "get-started/streaming/quickstart-streaming-java/", 
            "get-started/testing/",
            "get-started/about/",
            "tutorials/",
            "tutorials/agent-team/",
            "agents/",
            "agents/llm-agents/",
            "agents/workflow-agents/",
            "agents/workflow-agents/sequential-agents/",
            "agents/workflow-agents/loop-agents/",
            "agents/workflow-agents/parallel-agents/",
            "agents/custom-agents/",
            "agents/multi-agents/",
            "agents/models/",
            "tools/",
            "tools/function-tools/",
            "tools/built-in-tools/",
            "tools/third-party-tools/",
            "tools/google-cloud-tools/",
            "tools/mcp-tools/",
            "tools/openapi-tools/",
            "tools/authentication/",
            "runtime/",
            "runtime/runconfig/",
            "deploy/",
            "deploy/agent-engine/",
            "deploy/cloud-run/",
            "deploy/gke/",
            "sessions/",
            "sessions/session/",
            "sessions/state/",
            "sessions/memory/",
            "sessions/express-mode/",
            "callbacks/",
            "callbacks/types-of-callbacks/",
            "callbacks/design-patterns-and-best-practices/",
            "artifacts/",
            "events/",
            "context/",
            "observability/logging/",
            "observability/cloud-trace/",
            "observability/agentops/",
            "observability/arize-ax/",
            "observability/phoenix/",
            "observability/weave/",
            "evaluate/",
            "mcp/",
            "plugins/",
            "streaming/",
            "streaming/custom-streaming/",
            "streaming/custom-streaming-ws/",
            "streaming/dev-guide/part1/",
            "streaming/streaming-tools/",
            "streaming/configuration/",
            "grounding/google_search_grounding/",
            "grounding/vertex_ai_search_grounding/",
            "safety/",
            "a2a/",
            "a2a/intro/",
            "a2a/quickstart-exposing/",
            "a2a/quickstart-consuming/",
            "community/",
            "contributing-guide/",
            "api-reference/",
            "api-reference/cli/",
            "api-reference/python/",
            "api-reference/java/"
        ]
        
    def fetch_page(self, url_path):
        """Fetch a single page and return the content"""
        full_url = urljoin(self.base_url, url_path)
        try:
            print(f"Fetching: {full_url}")
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {full_url}: {e}")
            return None
    
    def html_to_markdown(self, html_content, page_url):
        """Convert HTML content to markdown"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the main article content
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='md-content')
        if not article:
            # Fallback to body if no article found
            article = soup.find('body')
        
        if not article:
            return "# Error\nCould not find main content in page."
            
        # Extract title
        title = soup.find('title')
        page_title = title.get_text().strip() if title else "Untitled"
        
        # Remove navigation, footer, and other non-content elements
        for element in article.find_all(['nav', 'header', 'footer', '.md-nav', '.md-sidebar']):
            element.decompose()
            
        markdown_content = f"# {page_title}\n\n"
        markdown_content += f"*Source: {page_url}*\n\n"
        
        # Process main content elements
        for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'code', 'blockquote', 'table']):
            markdown_content += self.process_element(element) + "\n\n"
        
        return markdown_content.strip()
    
    def process_element(self, element):
        """Convert an HTML element to markdown"""
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            text = element.get_text().strip()
            # Remove the ¶ symbol that appears in headers
            text = re.sub(r'\s*¶\s*', '', text)
            return f"{'#' * level} {text}"
            
        elif element.name == 'p':
            return self.process_text_content(element)
            
        elif element.name in ['ul', 'ol']:
            return self.process_list(element)
            
        elif element.name == 'pre':
            code = element.find('code')
            if code:
                language = ""
                # Try to extract language from class
                if code.get('class'):
                    for cls in code.get('class'):
                        if cls.startswith('language-'):
                            language = cls.replace('language-', '')
                            break
                return f"```{language}\n{code.get_text()}\n```"
            return f"```\n{element.get_text()}\n```"
            
        elif element.name == 'code' and element.parent.name != 'pre':
            return f"`{element.get_text()}`"
            
        elif element.name == 'blockquote':
            lines = element.get_text().strip().split('\n')
            return '\n'.join(f"> {line}" for line in lines)
            
        elif element.name == 'table':
            return self.process_table(element)
            
        else:
            return self.process_text_content(element)
    
    def process_text_content(self, element):
        """Process text content with inline formatting"""
        result = ""
        for item in element.contents:
            if hasattr(item, 'name'):
                if item.name == 'strong' or item.name == 'b':
                    result += f"**{item.get_text()}**"
                elif item.name == 'em' or item.name == 'i':
                    result += f"*{item.get_text()}*"
                elif item.name == 'code':
                    result += f"`{item.get_text()}`"
                elif item.name == 'a':
                    href = item.get('href', '')
                    text = item.get_text()
                    result += f"[{text}]({href})"
                else:
                    result += item.get_text()
            else:
                result += str(item)
        return result.strip()
    
    def process_list(self, element):
        """Process ul/ol lists"""
        items = []
        for li in element.find_all('li', recursive=False):
            item_text = self.process_text_content(li)
            if element.name == 'ul':
                items.append(f"- {item_text}")
            else:  # ol
                items.append(f"1. {item_text}")
        return '\n'.join(items)
    
    def process_table(self, table):
        """Process HTML tables to markdown"""
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for cell in tr.find_all(['th', 'td']):
                cells.append(cell.get_text().strip())
            if cells:
                rows.append('| ' + ' | '.join(cells) + ' |')
                
        if len(rows) > 0:
            # Add separator after header row
            if table.find('th'):
                header_sep = '|' + '---|' * len(rows[0].split('|')[1:-1]) + ''
                rows.insert(1, header_sep)
        
        return '\n'.join(rows)
    
    def save_documentation(self, output_dir="adk_docs_markdown"):
        """Scrape all pages and save as markdown files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        successful_pages = []
        failed_pages = []
        
        for page_path in self.pages:
            # Create filename from path
            if page_path == "":
                filename = "index.md"
            else:
                # Convert path to filename
                filename = page_path.rstrip('/').replace('/', '_') + ".md"
            
            filepath = os.path.join(output_dir, filename)
            
            # Fetch and convert page
            html_content = self.fetch_page(page_path)
            if html_content:
                markdown_content = self.html_to_markdown(html_content, urljoin(self.base_url, page_path))
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    successful_pages.append(page_path or "index")
                    print(f"✓ Saved: {filename}")
                except Exception as e:
                    print(f"✗ Error saving {filename}: {e}")
                    failed_pages.append(page_path or "index")
            else:
                failed_pages.append(page_path or "index")
                
            # Be respectful with delays
            time.sleep(1)
        
        # Create summary file
        summary_path = os.path.join(output_dir, "_SUMMARY.md")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# ADK Documentation Summary\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Successfully scraped pages ({len(successful_pages)}):\n\n")
            for page in successful_pages:
                f.write(f"- {page}\n")
            
            if failed_pages:
                f.write(f"\n## Failed pages ({len(failed_pages)}):\n\n")
                for page in failed_pages:
                    f.write(f"- {page}\n")
        
        print(f"\n📁 Documentation saved to: {output_dir}")
        print(f"✓ Successfully scraped: {len(successful_pages)} pages")
        if failed_pages:
            print(f"✗ Failed to scrape: {len(failed_pages)} pages")
        
        return output_dir, successful_pages, failed_pages

def main():
    """Main function to run the scraper"""
    scraper = ADKDocScraper()
    print("🚀 Starting ADK documentation scraping...")
    print(f"📄 Total pages to scrape: {len(scraper.pages)}")
    
    output_dir, successful, failed = scraper.save_documentation()
    
    print(f"\n🎉 Scraping completed!")
    print(f"📂 Output directory: {output_dir}")
    
if __name__ == "__main__":
    main()