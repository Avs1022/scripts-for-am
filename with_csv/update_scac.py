import ast
import requests
import json
import csv
import utils

# getting the desired files
csv_user_not_having_scac = open('user_not_having_scac.csv', 'r')
csv_user_used_for_updating_scac = open('user_used_for_updating_scac.csv', 'r')
csv_updated_users = open('updated_scac.csv', 'w')

# generating reader and writer
reader_user_not_having_scac = csv.reader(csv_user_not_having_scac)
reader_user_used_for_updating_scac = csv.reader(csv_user_used_for_updating_scac)
writer_updated_users = csv.writer(csv_updated_users)

header = ['FACILITY_NAME', 'FACILITY_ID', 'USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID',
          'USER_SCAC', 'USER_DATA_ACTUAL']

header2 = ['USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID', 'SCAC']

writer_updated_users.writerow(header)



# ['FACILITY_NAME', 'FACILITY_ID', 'USER_EMAIL', 'USER_ACTUAL_COMPANY_NAME', 'USER_ACTUAL_COMPANY_ID', 'USER_SCAC', 'USER_DATA_ACTUAL']

#      0                   1              2                   3                           4                      5              6

def update_carrier(carrier, company_id):
    params = {
        'company_id': company_id,
        'locale': 'en'
    }
    payload = ast.literal_eval(carrier[6]).copy()
    print(payload)
    key = utils.get_key(carrier[2], carrier[4])
    print(key)
    if key in scac_map:
        print('key is present')
        payload['scac'] = scac_map.get(key)
        payload['scacChanged'] = True
        payload['facility_id'] = carrier[1]
        url_for_updation = f'{utils.url_for_updating_carriers}{carrier[6]["fm_user_id"]}?'
        payload = json.dumps(payload)
        response = requests.request(url=url_for_updation, method='PUT', params=params, data=payload,
                                    auth=utils.get_auth())
        print(f'Trying to  update the user   {carrier["USER_EMAIL"]} for facility {carrier["FACILITY_NAME"]}')
        if response.status_code == 200:
            user_data = carrier.copy()
            user_data[5] = scac_map.get(key)
            print(f'successfully updated the user   {carrier[2]}')
            writer_updated_users.writerow(user_data)


scac_map = {}

row_index = 0
for row in reader_user_used_for_updating_scac:
    if row_index:
        print(row)
        key = utils.get_key(row[0], row[2])
        scac_map[key] = row[3]
    row_index += 1

row_index = 0
for row in reader_user_not_having_scac:
    if row_index:
        update_carrier(row, utils.companyId)
    row_index += 1
