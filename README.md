# 🕸️ Advanced Web Scraper

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.13.3-orange)
![Requests](https://img.shields.io/badge/Requests-2.32.3-brightgreen)
![GitHub last commit](https://img.shields.io/github/last-commit/TheRealSaiTama/WebScraper)

<img src="https://raw.githubusercontent.com/TheRealSaiTama/WebScraper/main/assets/webscraper_banner.png" alt="Web Scraper Banner" width="800">

_A powerful and flexible web scraping tool built with Python - extract data from any website with customizable selectors_

</div>

## ✨ Features

- 🔍 **Flexible CSS Selectors** - Dynamically configure which elements to scrape
- 🔄 **Scheduled Scraping** - Set up recurring scrapes at custom intervals
- 📊 **CSV Export** - Save extracted data directly to CSV format
- ⚡ **Rate Limiting** - Respectful scraping with built-in delays
- 🛡️ **Robust Error Handling** - Automatic retries and comprehensive logging
- 🌐 **Domain-Specific Optimizations** - Special handling for popular websites
- 📝 **Detailed Logging** - Track every step of the scraping process
- 🧩 **Modular Design** - Easy to extend and customize

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/TheRealSaiTama/WebScraper.git

# Navigate to the project directory
cd WebScraper

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage

Running the scraper is simple:

```bash
python scraper.py
```

You'll be prompted to:

1. Enter the URL to scrape
2. Choose whether to use custom CSS selectors
3. Enter the specific selectors for the data you want
4. Set up scheduled scraping (optional)

### 📝 Example

```
Enter the URL to scrape: https://example.com/products
Do you want to use custom CSS selectors? (y/n): y
Enter CSS selectors (leave blank to skip):
container selector: .product-item
title selector: .product-title
price selector: .product-price
Do you want to schedule periodic scraping? (y/n): y
Enter interval (e.g., '1h' for hourly, '30m' for 30 minutes, '1d' for daily): 1h
```

## 🏗️ Project Structure

```
WebScraper/
├── scraper.py          # Main scraper implementation
├── requirements.txt    # Project dependencies
├── output_*.csv        # Scraped data output files
├── scraper_*.log       # Detailed logging information
└── README.md           # Project documentation
```

## 🧠 Behind the Scenes

The WebScraper works through several sophisticated components:

### 📥 Data Fetching

The `fetchpage` method handles HTTP requests with:

- Configurable retries for transient failures
- Exponential backoff strategy
- User-agent rotation to avoid detection

### 🔍 Data Extraction

The `parsepage` method uses BeautifulSoup to:

- Navigate complex DOM structures
- Apply custom CSS selectors
- Extract text, attributes and links
- Handle malformed HTML gracefully

### ⏱️ Scheduling System

The `ScraperScheduler` class provides:

- Flexible scheduling intervals
- Persistent execution in the background
- Graceful shutdown handling

## 📊 Use Cases

- 🛒 **Price Monitoring** - Track prices of products across e-commerce websites
- 📰 **News Aggregation** - Collect articles from various news sources
- 🔬 **Research Data Collection** - Gather specific information for analysis
- 📊 **Market Analysis** - Collect data for market trends and analysis
- 🏆 **Sports Statistics** - Gather scores and player statistics

## 🛠️ Extending the Scraper

The modular design makes it easy to extend functionality:

```python
# Example: Adding a new data processor
def process_data(data):
    """Process the scraped data before saving"""
    # Your custom processing logic here
    return processed_data

# Then modify the main flow to include your processor
data = scraper.parsepage(html, selectors)
if data:
    data = process_data(data)
    scraper.save_to_csv(data, filename)
```

## ⚠️ Ethical Considerations

Please use this tool responsibly:

- ✅ Always respect robots.txt files
- ✅ Implement reasonable rate limiting
- ✅ Only scrape publicly accessible data
- ❌ Don't overload websites with requests
- ❌ Don't scrape personal or private information

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📃 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👤 Author

**TheRealSaiTama** - [GitHub Profile](https://github.com/TheRealSaiTama)

---

<div align="center">
  
[![Made with ❤️](https://forthebadge.com/images/badges/built-with-love.svg)](https://github.com/TheRealSaiTama)

</div>
