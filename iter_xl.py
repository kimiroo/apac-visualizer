import time
import random

import openpyxl

doc = openpyxl.open('Dataset.xlsx')
sheet = doc['Sheet1']

def get_random():
    plant_cnt = random.randint(0, 150)
    dealer_cnt = random.randint(0, 20)
    prj_rev = random.randint(10000, 700000000)
    act_rev = random.randint(10000, 700000000)
    tot_val = random.randint(10000000, 700000000000)

    market_potential = random.randint(0, 150)
    market_share = random.randint(0, 100) / 100

    return plant_cnt, dealer_cnt, prj_rev, act_rev, tot_val, market_potential, market_share


for row in sheet.iter_rows(3):
    for idx in range(0, 5):
        a, b, c, d, e, f, g = get_random()

        base_col_idx = (idx * 7) + 1

        row[base_col_idx + 0].value = a
        row[base_col_idx + 1].value = b
        row[base_col_idx + 2].value = c
        row[base_col_idx + 3].value = d
        row[base_col_idx + 4].value = e
        row[base_col_idx + 5].value = f
        row[base_col_idx + 6].value = g

doc.save('d2.xlsx')