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

# print(target_company.company_name)
# print("\n")
# print("Officers weighted-average score: "+str(round(target_company.officers_weighted_score(), 2)))
# print("\n")
# print("PSCs weighted-average score: "+str(round(target_company.pscs_weighted_score(), 2)))
# print("\n")
# print(json.dumps(target_company.summary_score, indent=4))
