import json

from model import Company, Analysis

ch_number = "06004999"

target_company = Company(company_number=ch_number)
analysis = Analysis(target_company)
analysis.get_api_data()

# TODO destination folder for binaries
# analysis.get_api_data(download_binary=True)

print(target_company.to_json())
print("\n")

print(target_company.company_name)
print("\n")
print("Officers weighted-average score: "+str(round(target_company.officers_weighted_score(), 2)))
print("\n")
print("PSCs weighted-average score: "+str(round(target_company.pscs_weighted_score(), 2)))
print("\n")
print(json.dumps(target_company.summary_score, indent=4))
