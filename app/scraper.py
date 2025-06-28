import asyncio
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class WebScraper:
    """Handles web scraping and document creation."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize text splitter for chunking large documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a single URL."""
        try:
            logger.info(f"Scraping URL: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Clean and validate content
            if not content or len(content.strip()) < 50:
                raise ValueError("Insufficient content extracted")
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'title': None,
                'content': None,
                'success': False,
                'error': str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML."""
        # Try different title sources
        title_sources = [
            lambda: soup.find('title').get_text().strip(),
            lambda: soup.find('h1').get_text().strip(),
            lambda: soup.find('meta', property='og:title')['content'],
            lambda: soup.find('meta', name='title')['content']
        ]
        
        for source in title_sources:
            try:
                title = source()
                if title:
                    return title
            except (AttributeError, TypeError, KeyError):
                continue
        
        return "No title found"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main'
        ]
        
        content = ""
        
        # Try to extract from main content areas first
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                break
        
        # Fallback to body content
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
        
        # Final fallback to all text
        if not content:
            content = soup.get_text(separator=' ', strip=True)
        
        # Clean up the content
        content = self._clean_content(content)
        
        return content
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize extracted content."""
        import re
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie.*?policy',
            r'Accept.*?cookies',
            r'Privacy.*?policy',
            r'Terms.*?service',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def create_documents(self, scraped_data: List[Dict[str, Any]]) -> List[Document]:
        """Convert scraped data to LangChain documents."""
        documents = []
        
        for data in scraped_data:
            if not data['success'] or not data['content']:
                continue
            
            try:
                # Create metadata
                metadata = {
                    'source': data['url'],
                    'title': data['title'],
                    'type': 'web_page'
                }
                
                # Split content into chunks if it's too long
                chunks = self.text_splitter.split_text(data['content'])
                
                # Create documents for each chunk
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_id'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    
                    doc = Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    )
                    documents.append(doc)
                
                logger.info(f"Created {len(chunks)} documents from {data['url']}")
                
            except Exception as e:
                logger.error(f"Error creating documents from {data['url']}: {e}")
                continue
        
        return documents
    
    async def scrape_urls_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs asynchronously."""
        loop = asyncio.get_event_loop()
        
        # Use ThreadPoolExecutor for CPU-bound scraping tasks
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                loop.run_in_executor(executor, self.scrape_url, url)
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Async scraping error: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs synchronously."""
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
        
        return results

# Global scraper instance
web_scraper = WebScraper()
