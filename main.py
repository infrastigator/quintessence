import json

from model import Company, Analysis

ch_number = "04542769"

target_company = Company(company_number=ch_number)
analysis = Analysis(target_company)
# 1. Basic get company raw data from all API endpoints
analysis.get_api_data()
# 2. Same as 1. + download all PDF documents to local output folder - will take longer
# analysis.get_api_data(download_binary=True)

print(target_company.to_json())

# 3. Get the scoring dataw
print(target_company.company_name)
print("\n")
print("Officers weighted-average score: "+str(round(target_company.officers_weighted_score(), 2)))
print("\n")
print("PSCs weighted-average score: "+str(round(target_company.pscs_weighted_score(), 2)))
print("\n")
print(json.dumps(target_company.summary_score, indent=4))
