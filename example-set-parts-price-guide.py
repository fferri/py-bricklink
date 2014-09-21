#!/usr/bin/env python
import bricklink

client = bricklink.ApiClient(
    # insert your keys here...
    '...',
    '...',
    '...',
    '...'
)

items = client.catalog.getSubsets('set','8043-1')

ks = ['quantity', 'item_no', 'item_category', 'item_type', 'item_name', 'color_id', 'is_alternate', 'min_price', 'avg_price', 'max_price','tot_min_price','tot_avg_price','tot_max_price']

print(';'.join(ks))
tot_min = 0; tot_avg = 0; tot_max = 0;
for item in items:
    row = {}
    entry = item['entries'][0]
    row['quantity'] = int(entry['quantity'])
    row['item_no'] = entry['item']['no']
    row['item_category'] = entry['item']['categoryID']
    row['item_type'] = entry['item']['type']
    row['item_name'] = entry['item']['name']
    row['color_id'] = entry['color_id']
    row['is_alternate'] = entry['is_alternate']
    price_guide = client.catalog.getPriceGuide(row['item_type'], row['item_no'], color_id=row['color_id'], region='europe', guide_type='sold', country_code='IT')
    row['min_price'] = float(price_guide['min_price'])
    row['avg_price'] = float(price_guide['avg_price'])
    row['max_price'] = float(price_guide['max_price'])
    row['tot_min_price'] = row['quantity']*row['min_price']
    row['tot_avg_price'] = row['quantity']*row['avg_price']
    row['tot_max_price'] = row['quantity']*row['max_price']
    tot_min += row['tot_min_price']
    tot_avg += row['tot_avg_price']
    tot_max += row['tot_max_price']
    print(';'.join(str(row[k]).replace(';','') for k in ks))

for k in ks: row[k] = ''
row['quantity'] = 'tot:'
row['tot_min_price'] = tot_min
row['tot_avg_price'] = tot_avg
row['tot_max_price'] = tot_max
print(';'.join(str(row[k]).replace(';','') for k in ks))
