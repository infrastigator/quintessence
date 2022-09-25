import sys
from model import Company, Analysis

ch_number = sys.argv[1]
flag = sys.argv[2]

target_company = Company(company_number=ch_number)
analysis = Analysis(target_company)

if flag == "binary":
    # Same as 1. + download all PDF documents to local output folder - will take longer
    analysis.get_api_data(download_binary=True)
elif flag == "basic":
    # Basic get company raw data from all API endpoints
    analysis.get_api_data()

# 3. Get the scoring data
analysis.score()
