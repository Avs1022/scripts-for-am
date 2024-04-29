username = 'automation@fourkites.com'
password = 'qaP@ssw0rd123'
companyId = 'shipper-sera'

url_facility_configuration = "https://dc-manager-configuration-service-qat.fourkites.com/api/v1/facility_configuration?"
url_for_fetching_carriers = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users?"
url_for_updating_carriers = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users/"


def get_key(email, actual_company_id):
    return f'{email}-**-{actual_company_id}'

def get_auth():
    return username, password
