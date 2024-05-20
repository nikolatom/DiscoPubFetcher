
# DiscoPubFetcher

DiscoPubFetcher is an automated tool for downloading PDFs of scientific papers using PubMed IDs (PMIDs). It fetches the articles from various journals and saves them in a specified directory. The tool uses Streamlit for the user interface and various web scraping techniques to find and download the PDF files.

## Features
- Upload a text file containing PMIDs or enter PMIDs manually.
- Automatically retries fetching articles up to a specified number of attempts.
- Generates a ZIP file containing all downloaded PDFs and a list of unfetched PMIDs.
- Download the results directly from the app.

## Installation

### Using pip

To use DiscoPubFetcher with pip, you need to have Python installed. You can install the required packages using the following command:

```bash
pip install streamlit requests beautifulsoup4
```

### Using Conda

To use DiscoPubFetcher with Conda, you need to have Conda installed. Follow these instructions to set up the environment:

1. Create a new Conda environment:

    ```bash
    conda create --prefix  ./env_discopubfetcher python=3.12
    ```

2. Activate the new environment:

    ```bash
    conda activate env_discopubfetcher
    ```

3. Install the required packages:

    ```bash
    pip install streamlit requests beautifulsoup4
    ```

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/nikolatom/discopubfetcher.git
    cd discopubfetcher
    ```

2. Run the Streamlit app:

    ```bash
    streamlit run discopubfetcher.py
    ```

3. Use the web interface to upload a file with PMIDs or enter PMIDs manually. Specify the output directory and the maximum number of retry attempts. Click the "Fetch Articles" button to start the process.

