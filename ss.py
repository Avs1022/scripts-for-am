import time

import requests
import pprint

username = 'automation@fourkites.com'
password = 'qaP@ssw0rd123'
companyId = 'shipper-sera'
url = "https://dc-manager-configuration-service-qat.fourkites.com/api/v1/facility_configuration?"
url2 = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users?"
url3 = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users/"
facility_list = []
scac_map = {}
user_not_having_scac = {}

log_user_having_scac = open('user_having_scac.txt', 'w')
log_user_not_having_scac = open('user_not_having_scac.txt', 'w')
log_updated_scac = open('updated_scac.txt', 'w')


def store_all_facilities(data):
    for facility in data['facilities']:
        facility_list.append(facility)
        user_not_having_scac[facility['facility_id']] = []


def get_auth():
    return username, password


def get_all_facilities(company_id):
    params = {
        "company_id": companyId,
        "locale": "en"}
    response = requests.request(method='GET', auth=get_auth(), url=url, params=params)
    store_all_facilities(response.json()['data'])


def get_key(email, actual_company_id):
    return f'{email}-**-{actual_company_id}'


def add_users(users, facility_id):
    log_user_having_scac.write(f'for {facility_id}\n')
    log_user_not_having_scac.write(f' for {facility_id}\n')
    for user in users:
        key = get_key(user['email'], user['actual_company_id'])
        scac = user['scac']
        if isinstance(scac, list) and len(scac) and key not in scac_map:
            scac_map[key] = scac
            log_user_having_scac.write(f'{user["email"]}      {user["actual_company_id"]}      {user["scac"]} \n')
        elif not isinstance(scac, list) or len(scac) == 0:
            user_not_having_scac[facility_id].append(user)
            log_user_not_having_scac.write(f'{user["email"]}      {user["actual_company_id"]}      {user["scac"]} \n')


def fetch_carriers(facility_id, company_id):
    params = {
        'facility_id': facility_id,
        'company_id': company_id,
        'collaborator_type': 'Carrier',
        'locale': 'en'
    }
    response = requests.request(method='GET', url=url2, auth=get_auth(), params=params)
    return response.json()['users']


def update_carrier(carrier, company_id, facility_id):
    params = {
        'company_id': company_id,
        'locale': 'en'
    }
    payload = carrier
    key = get_key(carrier["email"], carrier["actual_company_id"])
    if key in scac_map:
        print('key is present')
        payload['scac'] = scac_map.get(key)
        payload['scacChanged'] = True
        payload['facility_id'] = facility_id
        url_for_updation = f'{url3}{carrier["fm_user_id"]}?'
        print(f'url for updation {url_for_updation} \n')
        print(f'params for updation {params} \n')
        print(f'payload for updation {payload} \n')
        response = requests.request(url=url_for_updation, method='PUT', params=params, json=payload)
        if response.status_code == 200:
            log_updated_scac.write(f'\n {facility_id} \n {carrier["email"]} {pprint.pformat(payload)}\n')


# fetching all carriers one by one for different facilities
get_all_facilities(companyId)

# getting carriers for all facilities
for facility in facility_list:
    carriers = fetch_carriers(facility['facility_id'], companyId)
    add_users(carriers, facility['facility_id'])

#
for facility_id, users in user_not_having_scac.items():
    for user in users:
        update_carrier(user, companyId, facility_id)
log_user_having_scac.close()
log_user_not_having_scac.close()
log_updated_scac.close()