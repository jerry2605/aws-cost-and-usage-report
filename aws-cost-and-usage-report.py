#!/usr/bin/env python3

import argparse
import boto3
import datetime
import os
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=30)
args = parser.parse_args()


now = datetime.datetime.utcnow()
start = (now - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
end = now.strftime('%Y-%m-%d')

cd = boto3.client('ce', 'us-west-1')

results = []

token = None
while True:
    if token:
        kwargs = {'NextPageToken': token}
    else:
        kwargs = {}
    data = cd.get_cost_and_usage(TimePeriod={'Start': start, 'End':  end}, Granularity='DAILY', Metrics=['UnblendedCost'], GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}, {'Type': 'DIMENSION', 'Key': 'SERVICE'}], **kwargs)
    results += data['ResultsByTime']
    token = data.get('NextPageToken')
    if not token:
        break

path = os.getcwd()
os.makedirs(path+"//csv//", exist_ok=True)
with open(path + "//csv//" + 'results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
#saveFile = open(path + "//csv//" + 'results.csv','w', encoding='utf-8')

    print('\t'.join(['TimePeriod', 'LinkedAccount', 'Service', 'Amount', 'Unit', 'Estimated']))
    #saveFile.write('\t'.join(['TimePeriod', 'LinkedAccount', 'Service', 'Amount', 'Unit', 'Estimated'])+'\n')
    writer.writerow(['TimePeriod', 'LinkedAccount', 'Service', 'Amount', 'Unit', 'Estimated'])
    
    for result_by_time in results:
        for group in result_by_time['Groups']:
            amount = group['Metrics']['UnblendedCost']['Amount']
            unit = group['Metrics']['UnblendedCost']['Unit']
            print(result_by_time['TimePeriod']['Start'], '\t', '\t'.join(group['Keys']), '\t', amount, '\t', unit, '\t', result_by_time['Estimated'])
            record = result_by_time['TimePeriod']['Start'], group['Keys'][0],group['Keys'][1],  amount,  unit,  str(result_by_time['Estimated'])
            #for e in record:
               # saveFile.write(e)
            writer.writerow(record)
    
    print("results.csv is saved")
