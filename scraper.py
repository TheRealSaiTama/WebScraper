import requests
from bs4 import BeautifulSoup
import csv 
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import os
import json
from urllib.parse import urlparse
import schedule
import threading
from queue import Queue
import signal

def logsetup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filelog = f'scraper_{timestamp}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filelog),
            logging.StreamHandler()
        ]
    )

class RateLimiter:
    def __init__(self, calls: int = 1):
        self.calls = calls
        self.lastcall = time.time()
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.time()
            timepass = now - self.lastcall
            if timepass < 1.0 / self.calls:
                time.sleep(1.0 / self.calls - timepass)
            self.lastcall = time.time()

class WebScraper:
    def __init__(self, maxtry: int = 3, delay: int = 1, calls: int = 1):
        self.maxtry = maxtry
        self.delay = delay
        self.session = requests.Session()
        self.ratelimit = RateLimiter(calls)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetchpage(self, url: str) -> Optional[str]:
        for attempt in range(self.maxtry):
            try:
                self.ratelimit.wait()
                response = self.session.get(url)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1}/{self.maxtry} failed for {url}: {e}")
                if attempt < self.maxtry - 1:
                    time.sleep(self.delay * (attempt + 1))
                continue
        return None

    def parsepage(self, html: str, selectors: Dict[str, str]) -> List[Dict[str, str]]:
        if not html:
            logging.error("No HTML content to parse")
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        data = []
        
        containers = soup.select(selectors.get('container', '.item'))
        logging.info(f"Found {len(containers)} containers using selector: {selectors.get('container', '.item')}")
        
        if not containers:
            logging.warning("No containers found, trying to parse whole page")
            containers = [soup]
            
        for index, container in enumerate(containers, 1):
            itemdata = {}
            for field, selector in selectors.items():
                if field == 'container' or not selector:
                    continue
                try:
                    elements = container.select(selector)
                    if elements:
                        if field == 'title':
                            content = []
                            for element in elements:
                                text = element.get_text(strip=True)
                                if text:
                                    content.append(text)
                                tittleatrribute = element.get('title', '').strip()
                                if tittleatrribute:
                                    content.append(tittleatrribute)
                                if element.name == 'a':
                                    href = element.get('href', '').strip()
                                    if href:
                                        pathpart = href.rstrip('/').split('/')
                                        if pathpart:
                                            url_title = pathpart[-1].replace('-', ' ').title()
                                            content.append(url_title)
                            
                            itemdata[field] = ' | '.join(filter(None, content))
                        else:
                            itemdata[field] = ' | '.join(e.get_text(strip=True) for e in elements)
                        
                        logging.debug(f"Container {index}: Found content for {field}: {itemdata[field]}")
                    else:
                        logging.warning(f"Container {index}: No elements found for selector '{selector}' (field: {field})")
                        itemdata[field] = ''
                except Exception as e:
                    logging.error(f"Container {index}: Error extracting {field} using selector {selector}: {e}")
                    itemdata[field] = ''
            
            if any(itemdata.values()):
                data.append(itemdata)
                logging.info(f"Added item {len(data)}: {itemdata}")
            else:
                logging.warning(f"Container {index}: No data extracted, skipping")
        
        return data

    def save_to_csv(self, data: List[Dict[str, str]], filename: str) -> bool:
        if not data:
            logging.warning("No data to save")
            return False
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logging.info(f"Successfully wrote {len(data)} items to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving to CSV: {e}")
            return False

class ScraperScheduler:
    def __init__(self):
        self.scraper = WebScraper()
        self.running = False
        self.scheduled_jobs = []

    def schedule_job(self, url: str, selectors: Dict[str, str], interval: str):
        def job():
            logging.info(f"Running scheduled scrape for {url}")
            html = self.scraper.fetchpage(url)
            if html:
                data = self.scraper.parsepage(html, selectors)
                if data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'output_{timestamp}.csv'
                    self.scraper.save_to_csv(data, filename)

        value = int(interval[:-1])
        unit = interval[-1].lower()
        
        if unit == 'h':
            schedule.every(value).hours.do(job)
        elif unit == 'm':
            schedule.every(value).minutes.do(job)
        elif unit == 'd':
            schedule.every(value).days.do(job)
        else:
            raise ValueError("Invalid interval format. Use 'h' for hours, 'm' for minutes, 'd' for days")

        self.scheduled_jobs.append(job)

    def run(self):
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False

def handleoff(signum, frame):
    logging.info("Received shutdown signal. Stopping scheduler...")
    if hasattr(handleoff, 'scheduler'):
        handleoff.scheduler.stop()

def main():
    logsetup()
    logging.getLogger().setLevel(logging.DEBUG)
    
    signal.signal(signal.SIGINT, handleoff)
    signal.signal(signal.SIGTERM, handleoff)
    
    scheduler = ScraperScheduler()
    handleoff.scheduler = scheduler
    
    try:
        url = input("Enter the URL to scrape: ")
        if not urlparse(url).scheme:
            url = 'https://' + url
            
        customuse = input("Do you want to use custom CSS selectors? (y/n): ").lower() == 'y'
        if customuse:
            print("Enter CSS selectors (leave blank to skip):")
            selectors = {}
            
            container = input("container selector: ").strip()
            title = input("title selector: ").strip()
            price = input("price selector: ").strip()
            
            if container:
                selectors['container'] = container
            if title:
                selectors['title'] = title
            if price:
                selectors['price'] = price
                
        else:
            selectors = {
                'container': '.item',
                'title': '.title',
                'price': '.price'
            }
        
        schedulescrap = input("Do you want to schedule periodic scraping? (y/n): ").lower() == 'y'
        if schedulescrap:
            interval = input("Enter interval (e.g., '1h' for hourly, '30m' for 30 minutes, '1d' for daily): ")
            scheduler.schedule_job(url, selectors, interval)
            print(f"Scraper scheduled to run every {interval}")
            scheduler.run()
        else:
            logging.info(f"Starting one-time scrape of {url}")
            logging.info(f"Using selectors: {json.dumps(selectors, indent=2)}")
            
            html = scheduler.scraper.fetchpage(url)
            if html:
                preview = html[:500] + '...' if len(html) > 500 else html
                logging.debug(f"Received HTML content (preview): {preview}")
                
                data = scheduler.scraper.parsepage(html, selectors)
                if data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'output_{timestamp}.csv'
                    scheduler.scraper.save_to_csv(data, filename)
                else:
                    logging.error("No data extracted from the page")
            else:
                logging.error("Failed to fetch the page")
                
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.exception("Full error details:")
    finally:
        if schedulescrap:
            scheduler.stop()

if __name__ == "__main__":
    main()

