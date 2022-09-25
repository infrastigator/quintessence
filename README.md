# Rationale
* Unfinished business (WoW) and curiosity (KoS)
* Most of the Companies House data analysis out there is interesting but very much spaghetti duplicates - need for a central method given schema is stable

# Roadmap
* individual- or address-centric analysis rather than just company-centric (different starting point);
* officer reputation based on score for all companies involved with
* add other datasets (appointments, registers, charges, etc.)
* call to 3rd party APIs to get extra information (e.g., https://opencorporates.com/ for outside the UK);
* news mentions of individuals associated with a company of interest could use sentiment analysis (e.g., Tony Blair)
* percentile method to turn raw scores and subscores into percentile to help with interpretation
* deal with know bugs / limitations
  * deal with pagination
  * deal with name variation / string preprocessing / country to citizen
    * https://github.com/flyingcircusio/pycountry
    * https://github.com/knowitall/chunkedextractor/blob/master/src/main/resources/edu/knowitall/chunkedextractor/demonyms.csv
  * better exception handling / streamline method
