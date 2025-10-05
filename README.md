# DailyHFDataset

## Description
This project provides menu bar plugins for monitoring Hugging Face updates:
- **hf_news.1d.py**: Tracks and displays recent datasets from Hugging Face Hub with stats like downloads and likes.
- **hf_papers.1d.py**: Displays daily papers from Hugging Face, including titles, authors, upvotes, and summaries.

These are designed for tools like BitBar or xbar, showing notifications in your menu bar.

## Dependencies
- Python 3
- requests library (`pip install requests`)

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/DailyHFDataset.git
   ```
2. Install dependencies:
   ```
   pip install requests
   ```
3. Copy the scripts to your BitBar/xbar plugins directory (e.g., `~/.bitbar/`).
4. Make them executable:
   ```
   chmod +x hf_news.1d.py hf_papers.1d.py
   ```

## Usage
- Run the scripts via BitBar/xbar. They will fetch and display the latest Hugging Face datasets and papers in your menu bar.
- Click on items for more details or to open in browser.

## Author
MichaelPeng 

## License
This project is open source. Check repository for license details if available.
