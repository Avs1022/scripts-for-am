import requests
import json
import csv
import utils


facility_list = []
scac_map = {}
user_not_having_scac = {}
facility_map = {}
scac_used_for_updating_user = {}

# opening csv files
csv_user_having_scac = open('user_having_scac.csv', 'w')
csv_all_user = open('all_users.csv', 'w')
csv_user_not_having_scac = open('user_not_having_scac.csv', 'w')
csv_updated_users = open('updated_scac.csv', 'a')
csv_user_used_for_updating_scac = open('user_used_for_updating_scac.csv', 'w')
csv_invalid_user = open('invalid_user.csv','w')


# creating the writer
writer_user_having_scac = csv.writer(csv_user_having_scac)
writer_all_user = csv.writer(csv_all_user)
writer_user_not_having_scac = csv.writer(csv_user_not_having_scac)
writer_updated_users = csv.writer(csv_updated_users)
writer_user_used_for_updating_scac = csv.writer(csv_user_used_for_updating_scac)
writer_invalid_user = csv.writer(csv_invalid_user)

# HEADER FOR ALL CSV
header = ['FACILITY_NAME', 'FACILITY_ID', 'USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID',
          'USER_SCAC', 'USER_DATA']

# writing the header row
writer_user_having_scac.writerow(header)
writer_all_user.writerow(header)
writer_user_not_having_scac.writerow(header)
writer_updated_users.writerow(header)
writer_invalid_user.writerow(header)
writer_user_used_for_updating_scac.writerow(
    ['USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID', 'SCAC'])


# SCAC MAP STRUCTURE
# {
#     user_email:
#     user_actual_company_id:
#     user_actual_company_name
#     scac:
# }


# GETTING ALL THE FACILITIES FOR THE DESIRED COMPANIES
def store_all_facilities(data):
    for facility in data['facilities']:
        facility_map[facility['facility_id']] = facility['facility_name']
        facility_list.append(facility)
        user_not_having_scac[facility['facility_id']] = []



def get_entry(user, facility_id):
    keys = ['email', 'actual_company_name', 'actual_company_id', 'scac']
    entry = []
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
        "company_id": company_id,
        "locale": "en"
    }
    response = requests.request(method='GET', auth=utils.get_auth(), url=utils.url_facility_configuration, params=params)
    if response.status_code != 200:
        exit(1)
    store_all_facilities(response.json()['data'])


def get_missing_scac(list1, list2):
    set1 = set(list1)
    result = []
    for elem in list2:
        if elem not in set1:
            result.append(elem)
    return result


def check_user_is_valid(user):
    keys = ['email', 'actual_company_name', 'actual_company_id', 'scac']
    for key in keys:
        if key not in user:
            return False
    return True


def add_users(users, facility_id):
    for user in users:
        print("checking the facility ", facility_id)
        user_data = get_entry(user, facility_id)
        writer_all_user.writerow(user_data)
        if not check_user_is_valid(user):
            writer_invalid_user.writerow(user_data)
            continue
        key = utils.get_key(user['email'], user['actual_company_id'])
        scac = user['scac']
        scac_map_entry = {
            'scac': scac,
            'actual_company_id': user['actual_company_id'],
            'actual_company_name': user['actual_company_name'],
            'email': user['email']
        }
        if isinstance(scac, list) and len(scac) != 0:
            writer_user_having_scac.writerow(user_data)
            if key in scac_map:
                value = get_missing_scac(scac_map[key]['scac'], scac)
                scac_map[key]['scac'] = scac_map[key]['scac'] + value if len(value) != 0 else scac_map[key]['scac']
            else:
                scac_map[key] = scac_map_entry
        elif not isinstance(scac, list) or len(scac) == 0:
            writer_user_not_having_scac.writerow(user_data)


def fetch_carriers(facility_id, company_id):
    params = {
        'facility_id': facility_id,
        'company_id': company_id,
        'collaborator_type': 'Carrier',
        'locale': 'en'
    }
    response = requests.request(method='GET', url=utils.url_for_fetching_carriers, auth=utils.get_auth(), params=params)
    if response.status_code != 200:
        exit(1)
    return response.json()['users']



# fetching  all facilities for given company_id
get_all_facilities(utils.companyId)

# getting carriers for all facilities
for facility in facility_list:
    carriers = fetch_carriers(facility['facility_id'], utils.companyId)
    add_users(carriers, facility['facility_id'])

# adding the users with scac  which will be later used for updating the users which have scac = [] or scac = None
for key, value in scac_map.items():
    writer_user_used_for_updating_scac.writerow(
        [value['email'], value['actual_company_name'], value['actual_company_id'], value['scac']])


csv_all_user.close()
csv_updated_users.close()
csv_user_not_having_scac.close()
csv_user_having_scac.close()
csv_user_used_for_updating_scac.close()
