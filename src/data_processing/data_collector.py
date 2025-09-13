import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MisogynyDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.collected_data = []
        
    def scrape_academic_sources(self):
        """Scrape academic papers and research about misogynistic language"""
        sources = [
            {
                'name': 'JSTOR - Misogynistic Language Studies',
                'url': 'https://www.jstor.org/action/doBasicSearch?Query=misogynistic+language+detection',
                'parser': self._parse_jstor
            },
            {
                'name': 'Google Scholar - Gender Bias in Language',
                'url': 'https://scholar.google.com/scholar?q=misogynistic+language+detection+gender+bias',
                'parser': self._parse_google_scholar
            },
            {
                'name': 'Wikipedia - Misogyny',
                'url': 'https://en.wikipedia.org/wiki/Misogyny',
                'parser': self._parse_wikipedia
            }
        ]
        
        for source in sources:
            try:
                logger.info(f"Scraping {source['name']}")
                response = self.session.get(source['url'], timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data = source['parser'](soup)
                    self.collected_data.extend(data)
                    time.sleep(2)  # Be respectful
                else:
                    logger.warning(f"Failed to scrape {source['name']}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {str(e)}")
    
    def scrape_educational_resources(self):
        """Scrape educational websites about gender bias and inclusive language"""
        educational_sources = [
            {
                'name': 'UN Women - Gender-Inclusive Language',
                'url': 'https://www.unwomen.org/en/news/stories/2020/6/compilation-gender-inclusive-language',
                'parser': self._parse_un_women
            },
            {
                'name': 'APA Style - Bias-Free Language',
                'url': 'https://apastyle.apa.org/style-grammar-guidelines/bias-free-language',
                'parser': self._parse_apa_style
            }
        ]
        
        for source in educational_sources:
            try:
                logger.info(f"Scraping {source['name']}")
                response = self.session.get(source['url'], timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data = source['parser'](soup)
                    self.collected_data.extend(data)
                    time.sleep(2)
                else:
                    logger.warning(f"Failed to scrape {source['name']}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {str(e)}")
    
    def _parse_jstor(self, soup):
        """Parse JSTOR search results for misogynistic language research"""
        data = []
        articles = soup.find_all('div', class_='result-item')
        
        for article in articles:
            title_elem = article.find('h3')
            if title_elem:
                title = title_elem.get_text(strip=True)
                abstract_elem = article.find('div', class_='abstract')
                abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                
                data.append({
                    'source': 'JSTOR',
                    'type': 'academic_paper',
                    'title': title,
                    'content': abstract,
                    'category': 'research'
                })
        
        return data
    
    def _parse_google_scholar(self, soup):
        """Parse Google Scholar results for gender bias research"""
        data = []
        results = soup.find_all('div', class_='gs_r gs_or gs_scl')
        
        for result in results:
            title_elem = result.find('h3', class_='gs_rt')
            if title_elem:
                title = title_elem.get_text(strip=True)
                snippet_elem = result.find('div', class_='gs_rs')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                data.append({
                    'source': 'Google Scholar',
                    'type': 'academic_paper',
                    'title': title,
                    'content': snippet,
                    'category': 'research'
                })
        
        return data
    
    def _parse_wikipedia(self, soup):
        """Parse Wikipedia article on misogyny"""
        data = []
        content = soup.find('div', id='mw-content-text')
        
        if content:
            paragraphs = content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 50:  # Only meaningful paragraphs
                    data.append({
                        'source': 'Wikipedia',
                        'type': 'educational',
                        'title': 'Misogyny - Wikipedia',
                        'content': text,
                        'category': 'definition'
                    })
        
        return data
    
    def _parse_un_women(self, soup):
        """Parse UN Women's gender-inclusive language guide"""
        data = []
        content = soup.find('div', class_='content')
        
        if content:
            paragraphs = content.find_all(['p', 'li'])
            for elem in paragraphs:
                text = elem.get_text(strip=True)
                if text and len(text) > 20:
                    data.append({
                        'source': 'UN Women',
                        'type': 'guidelines',
                        'title': 'Gender-Inclusive Language Guidelines',
                        'content': text,
                        'category': 'guidelines'
                    })
        
        return data
    
    def _parse_apa_style(self, soup):
        """Parse APA Style bias-free language guidelines"""
        data = []
        content = soup.find('main')
        
        if content:
            sections = content.find_all(['h2', 'h3', 'p'])
            current_section = ""
            
            for elem in sections:
                if elem.name in ['h2', 'h3']:
                    current_section = elem.get_text(strip=True)
                elif elem.name == 'p':
                    text = elem.get_text(strip=True)
                    if text and len(text) > 30:
                        data.append({
                            'source': 'APA Style',
                            'type': 'guidelines',
                            'title': f'Bias-Free Language - {current_section}',
                            'content': text,
                            'category': 'guidelines'
                        })
        
        return data
    
    def create_misogyny_terms_dataset(self):
        """Create a structured dataset of misogynistic terms and alternatives"""
        misogyny_data = {
            'derogatory_terms': [
                {
                    'term': 'bitches',
                    'category': 'derogatory',
                    'severity': 'high',
                    'context': 'Used to demean or insult women',
                    'alternatives': ['women', 'people', 'individuals', 'colleagues'],
                    'explanation': 'This term is deeply misogynistic and reduces women to objects of contempt.',
                    'impact': 'Reinforces harmful stereotypes and contributes to gender inequality.'
                },
                {
                    'term': 'sluts',
                    'category': 'derogatory',
                    'severity': 'high',
                    'context': 'Used to shame women for sexual behavior',
                    'alternatives': ['people', 'individuals', 'women'],
                    'explanation': 'This term is used to control and shame women\'s sexuality.',
                    'impact': 'Perpetuates double standards and sexual shaming.'
                },
                {
                    'term': 'whores',
                    'category': 'derogatory',
                    'severity': 'high',
                    'context': 'Used to insult women based on perceived sexual behavior',
                    'alternatives': ['people', 'individuals', 'women'],
                    'explanation': 'This term is extremely offensive and dehumanizing.',
                    'impact': 'Reinforces harmful stereotypes about women\'s worth.'
                }
            ],
            'devaluing_terms': [
                {
                    'term': 'bossy',
                    'category': 'devaluing',
                    'severity': 'medium',
                    'context': 'Applied disproportionately to assertive women',
                    'alternatives': ['assertive', 'confident', 'decisive', 'leadership-oriented'],
                    'explanation': 'This term is often used to criticize women for the same qualities praised in men.',
                    'impact': 'Undermines women\'s leadership and confidence.'
                },
                {
                    'term': 'emotional',
                    'category': 'devaluing',
                    'severity': 'medium',
                    'context': 'Used to dismiss women\'s feelings and arguments',
                    'alternatives': ['passionate', 'concerned', 'invested', 'caring'],
                    'explanation': 'This term is used to invalidate women\'s legitimate concerns.',
                    'impact': 'Dismisses women\'s perspectives and experiences.'
                },
                {
                    'term': 'hysterical',
                    'category': 'devaluing',
                    'severity': 'high',
                    'context': 'Used to dismiss women\'s emotional responses',
                    'alternatives': ['upset', 'concerned', 'frustrated', 'passionate'],
                    'explanation': 'This term has a sexist history and is used to silence women.',
                    'impact': 'Undermines women\'s credibility and agency.'
                }
            ],
            'stereotypical_phrases': [
                {
                    'term': 'run like a girl',
                    'category': 'stereotypical',
                    'severity': 'medium',
                    'context': 'Reinforces traditional gender roles',
                    'alternatives': ['run with determination', 'run with effort', 'run with skill'],
                    'explanation': 'This phrase suggests that being feminine is inferior.',
                    'impact': 'Reinforces harmful gender stereotypes and limits girls\' confidence.'
                },
                {
                    'term': 'boys will be boys',
                    'category': 'stereotypical',
                    'severity': 'medium',
                    'context': 'Excuses male misbehavior',
                    'alternatives': ['people should be held accountable', 'behavior has consequences'],
                    'explanation': 'This phrase excuses harmful behavior and reinforces gender stereotypes.',
                    'impact': 'Normalizes problematic behavior and gender inequality.'
                }
            ],
            'objectification_terms': [
                {
                    'term': 'hot',
                    'category': 'objectification',
                    'severity': 'low',
                    'context': 'When used to describe women\'s appearance in professional contexts',
                    'alternatives': ['professional', 'capable', 'skilled', 'qualified'],
                    'explanation': 'Focusing on appearance in professional contexts is inappropriate.',
                    'impact': 'Reduces women to their appearance rather than their abilities.'
                },
                {
                    'term': 'sexy',
                    'category': 'objectification',
                    'severity': 'medium',
                    'context': 'When used to describe women in non-romantic contexts',
                    'alternatives': ['attractive', 'stylish', 'elegant', 'confident'],
                    'explanation': 'This term can be objectifying when used inappropriately.',
                    'impact': 'Can make women feel uncomfortable and objectified.'
                }
            ]
        }
        
        return misogyny_data
    
    def save_data(self, filename='collected_misogyny_data.json'):
        """Save collected data to JSON file"""
        # Add structured misogyny terms to collected data
        misogyny_terms = self.create_misogyny_terms_dataset()
        
        complete_data = {
            'scraped_content': self.collected_data,
            'misogyny_terms': misogyny_terms,
            'metadata': {
                'total_scraped_items': len(self.collected_data),
                'total_terms': len(misogyny_terms['derogatory_terms']) + 
                              len(misogyny_terms['devaluing_terms']) + 
                              len(misogyny_terms['stereotypical_phrases']) + 
                              len(misogyny_terms['objectification_terms']),
                'collection_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filename}")
        return complete_data

def main():
    """Main function to run the data collection"""
    collector = MisogynyDataCollector()
    
    logger.info("Starting misogyny data collection...")
    
    # Collect from academic sources
    collector.scrape_academic_sources()
    
    # Collect from educational resources
    collector.scrape_educational_resources()
    
    # Save all collected data
    data = collector.save_data()
    
    logger.info(f"Collection complete! Collected {len(data['scraped_content'])} items and {data['metadata']['total_terms']} misogyny terms.")
    
    return data

if __name__ == "__main__":
    main() 