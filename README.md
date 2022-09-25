# Quintessence

## Team Members
This tool has been developed by Morgan Hervé-Mignucci (https://github.com/infrastigator) and Sean Greaves (https://github.com/ribenamaplesyrup).
We developed the initial idea of a dedicated tool to aggregate and score Companies House data with Gabrielle (https://github.com/fractalcactus).

## Tool Description
The objective of _Quintessence_ is to provide OSINT researchers with a one-stop-shop tool to (1) easily get all the Companies House data available on a given company and (2) score a company based on how many red flags have been identified during this discovery and analysis process.

We've built this tool for two main reasons:
* The interesting Companies House data on a given company typically goes beyond the specific endpoint made available. There is more information available in the related API endpoints (for directors, persons with significant controls, filings, other appointments directors have, etc.) and in the actual documents. It's hard to make sense of all this information (we've either done this manually [a long time ago](https://www.climatepolicyinitiative.org/publication/san-giorgio-group-case-studies-walney-offshore-windfarms/) or more recently exploring using [a Jupyter notebook interface](https://github.com/ribenamaplesyrup/sugartrail)). We felt like a robust Companies House tool was missing from what's available out there, so we built one.
* Given how much data is available once you start pulling and organizing this information, having a set of transparent methods to identify red flags on companies and attempting to quantify a company based on how many red flags it has is a way to help researchers have a quick score to see if a given company is worth a second look or not.

## Installation
### Preliminary step
1. Make sure you have Python version 3.10 or greater installed;
2. Download the tool's repository using the command:

        git clone https://github.com/infrastigator/quintessence.git

3. You will need an API key from Companies House to authenticate with the API (create a live application from the developers section of their [website](https://developer.company-information.service.gov.uk/)).
Then you'll need to create a local file to store your key. If you're on Linux or Mac, you can do the following:

        cd quintessence
        touch .env
        nano .env
        # This will open the interactive shell to modify your file
        # type CH_API_KEY=PASTE_YOUR_API_KEY_HERE
        # and press CTRL+X to save and exit

## Usage
* **Note**: Open `Tutorial.ipynb` for a tour of the functionalities currently implemented.

To create a folder with the raw data and the score JSON

    # from the command line
    python main.py "11004735" "basic"

You can also add an optional flag to download all the PDF documents associated with this company (takes longer obviously)

    # from the command line
    python main.py "11004735" "binary"


## Additional Information
### Next Steps
Here's a list of features that we'd like to develop in the future
* better documentation and guided use cases - anything to make the user's life easier; 
* extract metadata from linked PDF and XHTML documents;
* OCR of PDF documents to extract interesting content;
* extract data from other API endpoints (appointments, registers, charges, etc.)
* score officers' reputation based on the score for all companies they're involved with (nominations and / or companies where they are Persons with Significant Control);
* integrate with 3rd party APIs to get extra information on companies outside the UK (e.g., https://opencorporates.com/);
* the news mentions of individuals associated with a company of interest could use sentiment analysis to avoid false positives;
* we'll turn the raw score into percentiles to help OSINT researches with interpreting the results;
* individual- or address-centric analysis rather than just company-centric (in other words, a different starting point for the analysis);
* general bug fixing and robustness (i.e., tests);

### Limitations
Here are some know bugs or limitations:
* pagination support is needed (if a company has more than 25 documents, directors, etc. - the data pulled will be limited to the first 25);
* for rules involving matching against names, countries, or citizenship, we need string pre-processing and fuzzy matching rules to avoid false negatives;
* in order to map citizenship / nationality to countries, we need to research and implement other packages ([1](https://github.com/flyingcircusio/pycountry), [2](https://github.com/knowitall/chunkedextractor/blob/master/src/main/resources/edu/knowitall/chunkedextractor/demonyms.csv)); 
* exception handling could be streamlined;
