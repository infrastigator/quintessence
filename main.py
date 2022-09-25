from model import Company, Analysis

ch_number = "11004735"

target_company = Company(company_number=ch_number)
analysis = Analysis(target_company)

# 1. Basic get company raw data from all API endpoints
analysis.get_api_data()

# 2. Same as 1. + download all PDF documents to local output folder - will take longer
# analysis.get_api_data(download_binary=True)

# 3. Get the scoring data
analysis.score()
