from datetime import date
import json
import os
import random
import time

from dotenv import load_dotenv
from GoogleNews import GoogleNews
import requests

# Loading environment variables
load_dotenv()
access_token = os.getenv('CH_API_KEY')

# Loading reference datasets
with open('datasets/red_flag_countries.json') as fp:
    red_flag_countries = json.load(fp)['red_flag_countries']

with open('datasets/fake_names.json') as fp:
    fake_names = json.load(fp)['fake_names']

with open('datasets/score_weights.json') as fp:
    score_weights = json.load(fp)

# API Endpoints
company_api = "https://api.company-information.service.gov.uk/company/"
document_api = "https://frontend-doc-api.company-information.service.gov.uk/document/"

# API Endpoints - company appendices (endpoint + company_number + appendix)
pscs_api_appendix = "/persons-with-significant-control"
officers_api_appendix = "/officers"
filing_history_api_appendix = "/filing-history"

# API Endpoints - document appendices (endpoint + document_id + appendix)
content_api = "/content"

# API Endpoints - officers appendices (endpoint + appointment_id + api)
appointment_api = "/appointments"

# WebSearch Endpoints
company_web = "https://find-and-update.company-information.service.gov.uk/company/"
company_search_web = "https://find-and-update.company-information.service.gov.uk/search?q="

# WebCheck Endpoints
# Note: old store that will be deprecated and without REST endpoints
company_store = "https://wck2.companieshouse.gov.uk//compdetails"


class Company:
    def __init__(self, company_number):
        self.company_number = company_number  # '11004735'
        self.company_name = None  # 'KINGDOM OF SWEETS LTD'
        self.type = None  # 'ltd'
        self.company_status = None  # 'active'
        self.jurisdiction = None  # 'england-wales'
        self.date_of_creation = None  # '2017-10-10'
        self.sic_codes = None  # ['47240']
        # Compliance
        self.can_file = None  # True
        self.has_charges = None  # False
        self.has_insolvency_history = None  # False
        self.accounts = None  # dictionary that could be parsed
        self.confirmation_statement = None  # dictionary that could be parsed
        # Section 790ZG (Companies Act 2006)
        self.has_super_secure_pscs = None  # False
        # Hash-like header attribute (useful to see if analysis needs refreshing)
        self.etag = None  # '29702aba64464ae3a28f6e921f5ff89599713cf8'
        # Individuals of interest
        self.total_pscs_count = None  # 1
        self.active_pscs_count = None  # 1
        self.ceased_pscs_count = None  # 0
        self.total_officers_count = None  # 1
        self.active_officers_count = None  # 1
        self.inactive_officers_count = None  # 0
        self.resigned_officers_count = None  # 0
        # "Foreign Keys"
        self.registered_office = None  # single object
        self.pscs = []  # list of objects
        self.officers = []  # list of objects
        self.filings = []  # list of objects
        # Output
        self.summary_score = {}

    def officers_weighted_score(self) -> float:
        if len(self.officers) > 0:
            officers_scores = []
            for officer in self.officers:
                if officer.officer_role == "director" or officer.officer_role == "secretary":
                    # Call score() method
                    officer.score(extra_search_term=self.company_name)
                    # Generate and print summary information
                    summary_string = "- " + officer.name + ": " + str(round(officer.summary_score, 2))
                    if len(officer.red_flags) > 0:
                        summary_string += " - (Red flags: "+", ".join(officer.red_flags)+")"
                    print(summary_string)
                    # Add to list
                    officers_scores.append(officer.summary_score)
                elif officer.officer_role == "corporate-secretary":
                    default_score = 0.0
                    summary_string = "- " + officer.name + ": " + str(round(default_score, 2))
                    print(summary_string)
                    officers_scores.append(default_score)
                elif officer.officer_role == "corporate-director":
                    default_score = 0.0
                    summary_string = "- " + officer.name + ": " + str(round(default_score, 2))
                    print(summary_string)
                    officers_scores.append(default_score)

            weighted_average = sum(officers_scores) / len(officers_scores)
            self.summary_score['officers'] = weighted_average
            return weighted_average

        else:
            # no officers
            # TODO actually just having no officers decreases your shadiness score
            return 0.0

    def pscs_weighted_score(self) -> float:
        if len(self.pscs) > 0:
            pscs_scores = []
            for psc in self.pscs:
                # Call score() method
                psc.score(extra_search_term=self.company_name)
                # Generate and print summary information
                summary_string = "- " + psc.name+": "+str(round(psc.summary_score, 2))
                if len(psc.red_flags) > 0:
                    summary_string += " - (Red flags: "+", ".join(psc.red_flags)+")"
                print(summary_string)
                # Add to list
                pscs_scores.append(psc.summary_score)

            weighted_average = sum(pscs_scores) / len(pscs_scores)
            self.summary_score['pscs'] = weighted_average
            return weighted_average

        else:
            # no PSCs
            # TODO actually just having no PSCs decreases your shadiness score
            return 0.0

    def directors_etc_are_just_not_here(self) -> bool:
        pass

    def company_has_weird_sic_code(self) -> bool:
        pass

    def company_is_in_compliance(self) -> bool:
        # TODO Are documents missing? No articles of incorporation
        # Is the company late on filing?
        # Past charges / insolvency
        pass

    def zombie_company(self) -> bool:
        # TODO Is the company dormant for more than x years / months?
        pass

    # TODO add method to calculate size of final object once populated

    def to_json(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)

    def __str__(self) -> str:
        if self.company_name:
            return self.company_name + " (" + self.company_number + ")"
        else:
            return self.company_name


class Address:
    def __init__(self):
        self.premises = None  # 'Burnard Accountants, 8 Bankside Building'
        self.address_line_1 = None  # '3rd Floor 13 Charles Ii Street'
        self.address_line_2 = None  # 'Station Road'
        self.postal_code = None  # 'SW1Y 4QU'
        self.locality = None  # 'London'
        self.region = None  # 'Greater London'
        self.country = None  # 'England'

    def has_fake_address(self) -> bool:
        # TODO use official Royal Mail API
        # TODO has inconsistencies between PostCode and Locality, etc.
        pass

    def has_generic_address(self) -> bool:
        # “Buckingham Palace”
        pass

    def __str__(self):
        return self.address_line_1


class RegisteredOffice(Address):
    def __init__(self):
        super().__init__()
        self.registered_office_is_in_dispute = None  # False
        self.undeliverable_registered_office_address = None  # False

    def has_high_proportion_short_lived_companies(self) -> bool:
        pass

    def has_high_proportion_of_dissolved_companies(self) -> bool:
        pass

    def has_high_proportion_of_fraudulent_businesses(self) -> bool:
        # fake registration farm
        pass


class Person:
    def __init__(self):
        self.id = None
        self.title = None  # 'Mr'
        self.forename = None  # 'Chase'
        self.middle_name = None  # 'James Bailey Earl'
        self.surname = None  # 'Manders'
        self.name = None  # 'Mr Chase James Bailey Earl Manders'
        self.nationality = None  # 'British'
        self.country_of_residence = None  # 'England'
        self.dob_year = None  # 1981
        self.dob_month = None  # 9
        self.etag = None  # 'c6c04d72359cd8c9700bc17193edfe5d272a2781'
        # "Foreign keys"
        self.address = None
        # Output
        self.summary_score = None
        self.red_flags = []

    def name_preprocessing(self) -> None:
        # for Officers, we just have self.name
        if "," in self.name:
            try:
                self.forename = self.name.split(', ')[1].split(' ')[0]
            except TypeError as e:
                print(e)
            try:
                self.surname = self.name.split(', ')[0].capitalize()
            except TypeError as e:
                print(e)
        else:
            pass

    def score(self, extra_search_term: str = None):
        # 0 = lowest risk vs. 100 = highest risk
        score = 0
        if self.is_disqualified_director():
            # Person is disqualified to be a director from official Companies House API
            score = 100
        # building blocks approach
        else:
            # name preprocessing
            self.name_preprocessing()

            if self.name_flag():
                # person's name is fake / is in bad reputation list / looks random
                score += 100 * score_weights["person"]["name_flag"]
            if self.news_mentions_flag(extra_search_term):
                # person's name is mentioned in the news
                score += 100 * score_weights["person"]["news_mentions_flag"]
            if self.nationality_flag():
                # person's nationality is from a list of red flag countries
                score += 100 * score_weights["person"]["nationality_flag"]
            if self.residence_flag():
                # person's country of residence is from a list of red flag countries
                score += 100 * score_weights["person"]["residence_flag"]
            if self.age_flag():
                # person's age is problematic
                score += 100 * score_weights["person"]["age_flag"]

        # Persist score as object attribute
        self.summary_score = score

        return score

    def is_disqualified_director(self) -> bool:
        # TODO https://find-and-update.company-information.service.gov.uk/register-of-disqualifications/
        return False

    def name_flag(self) -> bool:
        if self.name in fake_names:
            self.red_flags.append("individual names found in list of fake / generic names")
            return True
        else:
            return False

    def news_mentions_flag(self, extra_search_term: str = None) -> bool:
        news = []
        # sleep before using API to avoid blocking
        time.sleep(random.uniform(0, 2))
        googlenews = GoogleNews(period='10y')

        if self.forename and self.surname:
            # for PSCs (exact search operand with quotes)
            input_name = '"' + self.forename + " " + self.surname + '"'

        elif self.name:
            # for officers - no exact search since self.name not a typical way to refer to someone
            self.name_preprocessing()
            input_name = '"' + self.forename + " " + self.surname + '"'

        else:
            # Can't extract a valid input name
            return False

        if extra_search_term:
            input_name += ' ' + '"' + extra_search_term + '"'

        googlenews.get_news(input_name)
        for story in googlenews.results():
            if story['title'] not in news:
                news += [story['title']]

        print(input_name)
        print(news)

        if len(news) > 0:
            self.red_flags.append("news mentions of the individual")
            return True
        else:
            return False

    def residence_flag(self) -> bool:
        # Country of residence is a tax haven or country with financial sanctions (e.g. OFAC Sanction List)
        if self.country_of_residence in red_flag_countries:
            self.red_flags.append("country of residence in red flag countries")
            return True
        else:
            return False

    def nationality_flag(self) -> bool:
        # Country of nationality is a tax haven or country with financial sanctions (e.g. OFAC Sanction List)
        if self.nationality in red_flag_countries:
            self.red_flags.append("country of nationality in red flag countries")
            return True
        else:
            return False

    def age_flag(self) -> bool:
        # If too old or too young to be a director (but could still be a PSC?)
        if self.dob_year:
            current_age = date.today().year - self.dob_year
            if current_age < 18:
                self.red_flags.append("individual below 18")
            elif current_age > 70:
                self.red_flags.append("individual above 70")

            return current_age < 18 or current_age > 70

        else:
            # for older appointments there is no PII
            # TODO missing data provides a boost to final score
            return False

    def __str__(self) -> str:
        return self.name


class Officer(Person):
    def __init__(self):
        super().__init__()
        self.appointment = None
        self.appointed_on = None  # '2017-10-10'  - TODO appointment might be another object
        self.occupation = None  # 'Director'
        self.officer_role = None  # 'director'
        # self.appointments = None  # PK to list of all appointments "/officers/Nd2URspq4bvLy-hwzDZ0_p7FGJw/appointments"

    def is_professional(self):
        # TODO method to identify a “professional” corporate secretary services providers based on an official list
        pass

    def is_former_director(self):
        # TODO there was an appointment that ended
        pass

    def circular_or_multilayered_appointments(self):
        # TODO company is a directory of a company (that’s a director of a company…) - shell companies;
        pass

    def has_too_many_mandates(self):
        # TODO too many companies to handle for a single individual;
        pass

    def dissolves_a_lot(self):
        pass

    def sits_on_many_dormant_companies(self):
        pass


class PersonWithSignificantControl(Person):
    def __init__(self):
        super().__init__()
        self.kind = None  # 'individual-person-with-significant-control'
        self.notified_on = None  # '2017-10-10'
        self.nature_of_control = None  # ['ownership-of-shares-75-to-100-percent', 'voting-rights-75-to-100-percent', 'right-to-appoint-and-remove-directors']


class Filing:
    def __init__(self):
        self.transaction_id = None  # 'MzMyMDEyMDgxN2FkaXF6a2N4', 'QUFEUkw1SlZhZGlxemtjeA' - note: Not so random
        self.category = None  # 'confirmation-statement', 'capital', 'resolution', 'accounts', 'address', 'gazette', 'incorporation'
        self.filing_type = None  # 'CS01', 'SH01', 'RESOLUTIONS', 'AA', 'AA01' 'AD01', 'DISS40', 'GAZ1', 'NEWINC'  - What is this?
        self.description = None  # 'confirmation-statement-with-updates', 'capital-allotment-shares', 'resolution', 'accounts-with-accounts-type-dormant', 'change-account-reference-date-company-current-extended', 'change-registered-office-address-company-with-date-old-address-new-address', 'gazette-filings-brought-up-to-date', 'gazette-notice-compulsory', 'incorporation-company'
        self.action_date = None  # '2021-10-09', '2021-09-27'
        self.date = None  # '2021-11-14', '2021-10-11'
        self.paper_filed = None  # True - Could be used as hint that OCR might be less precise?
        # Frontend filing type-specific dictionaries to unpack when available
        self.associated_filings = None  # NEWINC - 'associated_filings': [{'action_date': 1507593600000, 'category': 'capital', 'date': '2017-10-10', 'description': 'statement-of-capital', 'description_values': {'capital': [{'currency': 'GBP', 'figure': '100'}], 'date': '2017-10-10'}, 'type': 'SH01'},{'category': 'incorporation', 'date': '2017-10-10', 'description': 'model-articles-adopted', 'type': 'MODEL ARTICLES'}],
        self.resolutions = None  # RESOLUTIONS [{'category': 'capital', 'description': 'resolution-removal-pre-emption', 'subcategory': 'resolution', 'type': 'RES11'}, {'category': 'capital', 'description': 'resolution-securities', 'subcategory': 'resolution', 'type': 'RES10'}],
        self.description_values = None  # {'made_up_date': '2021-10-09'}, {'date': '2021-09-27', 'capital': [{'figure': '718', 'currency': 'GBP'}]}, {'description': 'Resolutions'}, {'made_up_date': '2020-12-31'}
        # "Foreign Keys"
        self.document = None

    def __str__(self):
        if self.filing_type:
            return str(self.filing_type) + " (" + self.transaction_id + ")"
        else:
            return self.transaction_id


class Document:
    def __init__(self):
        self.document_id = None  # ZFCeh9wBOCh1lchgNjlGhQfzZFn2VDrodCW8hxwoMzU
        self.barcode = None  # 'XAH8U7F5', 'AAE6WDJN', None (when None does it mean there's no document attached?)
        self.pages = None  # 4, 1, 6
        self.category = None  # "annual-returns", "capital", "miscellaneous", "accounts", "registered-office-change", "new-companies"
        self.significant_date = None  # null, "2020-12-31T00:00:00Z"
        self.significant_date_type = None  # "", "made-up-date"
        self.filename = None  # "11004735_cs01_2021-11-14", "" (not always available), "11004735_aa_2021-09-29", "11004735_ad01_2021-07-23"
        self.created_at = None  # "2021-11-14T15:18:13.121316729Z" The date and time the document was first created
        self.updated_at = None  # The date and time the document was last updated
        self.etag = None  # "" The ETag of the resource
        # Available file types
        self.pdf = None  # bool if "application/pdf" is an available type
        self.pdf_content_length = None  # The size of the document when returned as this content-type
        self.json = None  # bool if "application/json" is an available type
        self.json_content_length = None  # The size of the document when returned as this content-type
        self.xml = None  # bool if "application/xml" is an available type
        self.xml_content_length = None  # The size of the document when returned as this content-type
        self.xhtml = None  # bool if "application/xhtml+xml" is an available type
        self.xhtml_content_length = None  # The size of the document when returned as this content-type
        self.csv = None  # bool if "text/csv" is an available type
        self.csv_content_length = None  # The size of the document when returned as this content-type
        # Actual content
        # TODO will return PDF by default but eventually replace by different types
        self.binary = None

    # Helper function
    def parse_pdf(self):
        # TODO OCR + parse + extract JSON
        # old school OCR like Tesseract or more modern ML to turn other PDF / rasterized images into text
        pass

    def parse_xhtml(self):
        # TODO there's a schema use it (http://www.hmrc.gov.uk/schemas)
        pass

    def extract_metadata(self):
        # file, head, version, hash, AWS S3 URI, etc.
        # TODO At some point we could even get a hash of the known fraudulent document;
        # Metadata of file / binary (not source code) + common patterns;
        pass

    # (1) Administrative Analysis
    def document_has_inconsistent_info_with_company(self):
        # Inconsistent address with registration address from above;
        pass

    # (2) Financial Analysis (note might require more than a document instance)
    def company_shareholding(self):
        # TODO generate cap table for a given date
        pass

    def company_generates_losses(self):
        pass

    def company_outlier_numbers(self):
        pass

    # (3) Forensic Analysis
    def document_is_generic(self):
        # “Templates” financial documents
        pass

    def __str__(self):
        return self.document_id


class Analysis:
    def __init__(self, company: Company):
        self.company = company

    # Helper function
    def api_get_request(self, target_endpoint: str, document_id: str = None) -> json:
        if target_endpoint == 'company':
            target_url = company_api + self.company.company_number
        elif target_endpoint == 'pscs':
            target_url = company_api + self.company.company_number + pscs_api_appendix
        elif target_endpoint == 'officers':
            target_url = company_api + self.company.company_number + officers_api_appendix
        elif target_endpoint == 'filings':
            target_url = company_api + self.company.company_number + filing_history_api_appendix
        elif target_endpoint == 'document':
            target_url = document_api + document_id
        elif target_endpoint == 'document_content':
            target_url = document_api + document_id + content_api
            # TODO modify Accept request parameter to match Content-Type - to get xhtml instead of pdf
            # https://developer-specs.company-information.service.gov.uk/document-api/reference/document-location/fetch-a-document

        # elif target_endpoint == 'appointments':
        #     target_url = company_api + self.company.company_number + officers_api_appendix + "/" + "Nd2URspq4bvLy-hwzDZ0_p7FGJw" + appointment_api
            # target_url = company_api + self.company.company_number + appointment_api + "DaGJaQyWRC-RgllvsMMKPprfNHc"
            # WFDGm9WCMXDcz4hkc92RPWayyWo
            # DaGJaQyWRC-RgllvsMMKPprfNHc "id"
            # Nd2URspq4bvLy-hwzDZ0_p7FGJw "appointment"
            # print(target_url)

        else:
            target_url = '/'
            print('select a valid target endpoint')

        response = requests.get(
            target_url,
            auth=requests.auth.HTTPBasicAuth(access_token, '')
        )

        if target_endpoint == 'document_content':
            return response.content  # return PDF binary
        else:
            return response.json()

    # Wrapper
    def get_api_data(self, download_binary: bool = False) -> None:
        # wrapper function to gather data from the various endpoints

        # 1. Data from Company endpoint
        self.get_api_company_data()

        # 2. Data from PSCS endpoint
        self.get_api_pscs_data()

        # 3. Data from Officers endpoint
        self.get_api_officers_data()

        # 4. Data from Filings History, Document, and Document Content endpoints
        if download_binary:
            self.get_api_filings_data(download_binary=True)
        else:
            self.get_api_filings_data()

    # Parsing of API data
    def get_api_company_data(self) -> None:
        api_data = self.api_get_request('company')

        # Company data
        try:
            self.company.company_name = api_data['company_name']
        except (KeyError, TypeError) as e:
            # TODO better message
            pass

        try:
            self.company.type = api_data['type']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.company_status = api_data['company_status']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.jurisdiction = api_data['jurisdiction']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.date_of_creation = api_data['date_of_creation']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.sic_codes = api_data['sic_codes']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.can_file = api_data['can_file']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.has_charges = api_data['has_charges']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.has_insolvency_history = api_data['has_insolvency_history']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.has_super_secure_pscs = api_data['has_super_secure_pscs']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.accounts = api_data['accounts']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.confirmation_statement = api_data['confirmation_statement']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.etag = api_data['etag']
        except (KeyError, TypeError) as e:
            pass

        # Registered Office data
        self.company.registered_office = RegisteredOffice()

        try:
            self.company.registered_office.address_line_1 = api_data['registered_office_address']['address_line_1']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.address_line_2 = api_data['registered_office_address']['address_line_2']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.postal_code = api_data['registered_office_address']['postal_code']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.country = api_data['registered_office_address']['country']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.locality = api_data['registered_office_address']['locality']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.region = api_data['registered_office_address']['region']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.registered_office_is_in_dispute = api_data['registered_office_is_in_dispute']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.registered_office.undeliverable_registered_office_address = api_data['undeliverable_registered_office_address']
        except (KeyError, TypeError) as e:
            pass

    def get_api_pscs_data(self) -> None:
        api_data = self.api_get_request('pscs')
        if not 'errors' in api_data:
        # if True:

            # Company data
            try:
                self.company.total_pscs_count = api_data['total_results']
            except (KeyError, TypeError) as e:
                pass

            try:
                self.company.active_pscs_count = api_data['active_count']
            except (KeyError, TypeError) as e:
                pass

            try:
                self.company.ceased_pscs_count = api_data['ceased_count']
            except (KeyError, TypeError) as e:
                pass

            # PSCS
            print(api_data)
            for item in api_data['items']:
                psc = PersonWithSignificantControl()

                try:
                    # extracting individual Primary Key from self link URI
                    # TODO is this a PSCS specific ID?
                    psc.id = item['links']['self'].split('/')[-1]
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.country_of_residence = item['country_of_residence']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.etag = item['etag']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.notified_on = item['notified_on']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.dob_month = item['date_of_birth']['month']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.dob_year = item['date_of_birth']['year']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.nature_of_control = item['nature_of_control']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.nationality = item['nationality']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.title = item['name_elements']['title']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.forename = item['name_elements']['forename']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.middle_name = item['name_elements']['middle_name']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.surname = item['name_elements']['surname']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.name = item['name']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.kind = item['kind']
                except (KeyError, TypeError) as e:
                    pass

                # Address
                psc.address = Address()

                try:
                    psc.address.premises = item['address']['premises']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.address_line_1 = item['address']['address_line_1']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.address_line_2 = item['address']['address_line_2']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.postal_code = item['address']['postal_code']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.locality = item['address']['locality']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.region = item['address']['region']
                except (KeyError, TypeError) as e:
                    pass

                try:
                    psc.address.country = item['address']['country']
                except (KeyError, TypeError) as e:
                    pass

                self.company.pscs.append(psc)

    def get_api_officers_data(self) -> None:
        api_data = self.api_get_request('officers')

        # Company data
        try:
            self.company.total_officers_count = api_data['total_results']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.active_officers_count = api_data['active_count']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.inactive_officers_count = api_data['inactive_count']
        except (KeyError, TypeError) as e:
            pass

        try:
            self.company.resigned_officers_count = api_data['resigned_count']
        except (KeyError, TypeError) as e:
            pass

        # Officers
        for item in api_data['items']:
            officer = Officer()

            try:
                # extracting individual Primary Key from self link URI
                officer.id = item['links']['self'].split('/')[-1]
            except (KeyError, TypeError) as e:
                pass

            try:
                # extracting individual Primary Key from officer appointments URI
                officer.appointment = item['links']['officer']['appointments'].split('/')[-2]
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.appointed_on = item['appointed_on']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.nationality = item['nationality']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.dob_month = item['date_of_birth']['month']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.dob_year = item['date_of_birth']['year']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.officer_role = item['officer_role']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.occupation = item['occupation']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.country_of_residence = item['country_of_residence']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.name = item['name']
            except (KeyError, TypeError) as e:
                pass

            # Address
            officer.address = Address()

            try:
                officer.address.premises = item['address']['premises']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.address_line_1 = item['address']['address_line_1']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.address_line_2 = item['address']['address_line_2']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.postal_code = item['address']['postal_code']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.locality = item['address']['locality']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.region = item['address']['region']
            except (KeyError, TypeError) as e:
                pass

            try:
                officer.address.country = item['address']['country']
            except (KeyError, TypeError) as e:
                pass

            self.company.officers.append(officer)

    def get_api_filings_data(self, download_binary: bool = False) -> None:
        api_data = self.api_get_request('filings')
        print(json.dumps(api_data, indent=4))
        # if not api_data['errors']:

        # Filings
        for item in api_data['items']:
            filing = Filing()

            try:
                filing.transaction_id = item['transaction_id']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.category = item['category']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.filing_type = item['type']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.description = item['description']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.action_date = item['action_date']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.date = item['date']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.paper_filed = item['paper_filed']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.description_values = item['description_values']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.resolutions = item['resolutions']
            except (KeyError, TypeError) as e:
                pass

            try:
                filing.associated_filings = item['associated_filings']
            except (KeyError, TypeError) as e:
                pass

            # Document
            # NOTE: some old documents don't have a document metadata
            try:
                if item['links']['document_metadata']:
                    document = Document()

                    try:
                        # extracting document Primary Key from URI
                        document.document_id = item['links']['document_metadata'].split('/')[-1]
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.pages = item['pages']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.barcode = item['barcode']
                    except (KeyError, TypeError) as e:
                        pass

                    # API call to Document endpoint to retrieve extra information on this document
                    document_api_data = self.api_get_request('document', document.document_id)

                    try:
                        document.category = document_api_data['category']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.significant_date = document_api_data['significant_date']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.significant_date_type = document_api_data['significant_date_type']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.filename = document_api_data['filename']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.created_at = document_api_data['created_at']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.updated_at = document_api_data['updated_at']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        document.etag = document_api_data['etag']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        if document_api_data['resources']['application/pdf']:
                            document.pdf = True
                            document.pdf_content_length = document_api_data['resources']['application/pdf']['content_length']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        if document_api_data['resources']['application/json']:
                            document.json = True
                            document.json_content_length = document_api_data['resources']['application/json']['content_length']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        if document_api_data['resources']['application/xml']:
                            document.xml = True
                            document.xml_content_length = document_api_data['resources']['application/xml']['content_length']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        if document_api_data['resources']['application/xhtml+xml']:
                            document.xhtml = True
                            document.xhtml_content_length = document_api_data['resources']['application/xhtml+xml']['content_length']
                    except (KeyError, TypeError) as e:
                        pass

                    try:
                        if document_api_data['resources']['text/csv']:
                            document.csv = True
                            document.csv_content_length = document_api_data['resources']['text/csv']['content_length']
                    except (KeyError, TypeError) as e:
                        pass

                    # optional API call to Document Content endpoint to retrieve binary for document
                    if download_binary:
                        time.sleep(5)
                        try:
                            document.binary = self.api_get_request('document_content', document.document_id)
                        except (KeyError, TypeError) as e:
                            pass

                filing.document = document

            except KeyError as e:
                pass

            self.company.filings.append(filing)

    # Scoring Method
    def score(self) -> int:
        # wrapper method that call the score methods in the correct order
        # and return the final score + percentile
        # TODO cross-cutting scoring
        #  while adding individual items (e.g. Company Name)

        # Reputation / Shadyness Score
        # TODO scoring tree based approach
        #  - company
        #  - individuals
        #  - addresses
        # percentile all this
        # leverages a JSON or YAML file that is loaded in memory and can be adjusted by users
        pass

    # Optional HTML reporting
    def report(self):
        # HTML
        pass
