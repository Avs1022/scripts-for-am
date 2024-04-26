import requests
import json
import csv
import pprint


# WORKING - UPDATES THE SCAC FOR CARRIER USERS IF THE SCAC IS [] OR None
# LOGIC -  ITERATE THROUGH ALL THE USERS
#          IF THE USER HAS SCAC FILLED CHECK IF THE USER WITH THAT MAIL AND ACTUAL COMPANY ID
#          IS PRESENT IN DICTIONARY OR NOT , IF NOT THEN STORE THE USER ,
#          ELSE IF THE USER DON'T HAVE SCAC ADD IT TO A LIST
#          THEN ONE BY ONE UPDATE THE USER WHICH DON'T HAVE SCAC BY GETTING IT FROM DICTIONARY
#          IF THE SCAC FOR THAT USER FOR THAT COMPANY IS NOT PRESENT THEN LEAVE THAT USER




username = 'automation@fourkites.com'
password = 'qaP@ssw0rd123'
companyId = 'shipper-sera'

url = "https://dc-manager-configuration-service-qat.fourkites.com/api/v1/facility_configuration?"
url2 = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users?"
url3 = "https://dc-manager-user-service-qat.fourkites.com/api/v1/users/"

facility_list = []
scac_map = {}
user_not_having_scac = {}
facility_map = {}

# opening csv files
csv_user_having_scac = open('user_having_scac.csv', 'w')
csv_all_user = open('all_users.csv', 'w')
csv_user_not_having_scac = open('user_not_having_scac.csv', 'w')
csv_updated_users = open('updated_scac.csv', 'w')
csv_user_used_for_updating_scac = open('user_used_for_updating_scac.csv', 'w')

# creating the writer
writer_user_having_scac = csv.writer(csv_user_having_scac)
writer_all_user = csv.writer(csv_all_user)
writer_user_not_having_scac = csv.writer(csv_user_not_having_scac)
writer_updated_users = csv.writer(csv_updated_users)
writer_user_used_for_updating_scac = csv.writer(csv_user_used_for_updating_scac)

# HEADER FOR ALL CSV
header = ['FACILITY_NAME', 'FACILITY_ID', 'USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID',
          'USER_SCAC', 'USER_DATA']

# writing the header row
writer_user_having_scac.writerow(header)
writer_all_user.writerow(header)
writer_user_not_having_scac.writerow(header)
writer_updated_users.writerow(header)
writer_user_used_for_updating_scac.writerow(header)

# GETTING ALL THE FACILITIES FOR THE DESIRED COMPANIES
def store_all_facilities(data):
    for facility in data['facilities']:
        facility_map[facility['facility_id']] = facility['facility_name']
        facility_list.append(facility)
        user_not_having_scac[facility['facility_id']] = []


def get_auth():
    return username, password

def get_entry(user, facility_id):
    keys = ['email', 'actual_company_name' , 'actual_company_id' , 'scac']
    entry =[]
    entry.append(facility_map.get(facility_id))
    entry.append(facility_id)
    for key in keys:
        if key in user:
            entry.append(user[key])
        else:
            entry.append(None)
    entry.append(user)
    return entry

def get_all_facilities(company_id):
    params = {
        "company_id": companyId,
        "locale": "en"
    }
    response = requests.request(method='GET', auth=get_auth(), url=url, params=params)
    if response.status_code != 200:
        exit(1)
    store_all_facilities(response.json()['data'])


def get_key(email, actual_company_id):
    return f'{email}-**-{actual_company_id}'


def add_users(users, facility_id):
    for user in users:
        # print(facility_map.get(facility_id))
        # pprint.pprint(user)
        user_data = get_entry(user,facility_id)
        # user_data = [facility_map.get(facility_id), facility_id, user["email"], user["actual_company_name"],
        #              user["actual_company_id"], user["scac"], user]
        writer_all_user.writerow(user_data)
        key = get_key(user['email'], user['actual_company_id'])
        scac = user['scac']
        if isinstance(scac, list) and len(scac):
            writer_user_having_scac.writerow(user_data)

        if isinstance(scac, list) and len(scac) and key not in scac_map:
            writer_user_used_for_updating_scac.writerow(user_data)
            scac_map[key] = scac
        elif not isinstance(scac, list) or len(scac) == 0:
            user_not_having_scac[facility_id].append(user)
            writer_user_not_having_scac.writerow(user_data)


def fetch_carriers(facility_id, company_id):
    params = {
        'facility_id': facility_id,
        'company_id': company_id,
        'collaborator_type': 'Carrier',
        'locale': 'en'
    }
    response = requests.request(method='GET', url=url2, auth=get_auth(), params=params)
    if response.status_code != 200:
        exit(1)
    return response.json()['users']


# updating the carrier user scac
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
        print(f'params for updation {params} \n')
        print(f'payload for updation {payload} \n')
        payload = json.dumps(payload)
        response = requests.request(url=url_for_updation, method='PUT', params=params, data=payload, auth=get_auth())
        print(f'url for updation {response.url} \n')
        print(response.json())
        user_data = get_entry(payload , facility_id)
        # user_data = [facility_map.get(facility_id), facility_id, carrier["email"], carrier["actual_company_name"],
        #              carrier["actual_company_id"], payload["scac"], payload]
        print(f'Trying to  update the user   {carrier["email"]} for facility {facility_map.get(facility_id)}')
        if response.status_code == 200:
            print(f'successfully updated the user   {carrier["email"]}')
            writer_updated_users.writerow(user_data)


# fetching all carriers one by one for different facilities
get_all_facilities(companyId)

# getting carriers for all facilities
for facility in facility_list:
    carriers = fetch_carriers(facility['facility_id'], companyId)
    add_users(carriers, facility['facility_id'])

# updating the users which either scac as empty or None
for facility_id, users in user_not_having_scac.items():
    for user in users:
        update_carrier(user, companyId, facility_id)


csv_all_user.close()
csv_updated_users.close()
csv_user_not_having_scac.close()
csv_user_having_scac.close()
csv_user_used_for_updating_scac.close()
