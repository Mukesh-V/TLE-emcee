import json
import time
import os

def removeEmpty(arr):
    for item in arr:
        if item == '':
            arr.remove('')
    return arr

def formatBSTAR(line1data):
    line1data = removeEmpty(line1data)
    line1data = removeEmpty(line1data)
    val = line1data[6]
    try:
        i = val.rindex('-')
    except:
        i = val.rindex('+')
    return float(val[:i] + "e" + val[i:])

labels = []
for item in sorted(os.listdir('./celestrak/')):
    with open('./celestrak/' + item) as file:
        lines = file.readlines()
        i = 0
        while i < len(lines) :
            label = {}
            label['name']  = lines[i].strip()
            label['line1'] = lines[i+1][:-1]
            label['line2'] = lines[i+2][:-1]
            label['drg']  = formatBSTAR(lines[i+1].split(' '))

            line2data = lines[i+2].split(' ')
            # I dont know why it takes 2 function calls to remove ''
            line2data = removeEmpty(line2data)
            line2data = removeEmpty(line2data)
            if len(line2data) == 8:
                line2data[7] = round(float(line2data[7]), 8)
            
            label['inc'] = float(line2data[2])
            label['ran'] = float(line2data[3])
            # Eccentricity seemed to miss the decimal point
            label['ecc'] = float('0.'+line2data[4])
            label['aop'] = float(line2data[5])
            label['man']  = float(line2data[6])
            label['mmo']  = float(line2data[7])

            # Calculating semi-major axis from Mean Motion
            # https://space.stackexchange.com/a/18291
            mu = 3.986004418e14
            pi = 3.141592653
            a = ( mu ** (1/3) )/ ( (2*label['mmo']*pi / 86400) ** (2/3) )
            label['sma'] = round(a/1000, 5)

            labels.append(label)
            i += 3

file = open('labels.json', 'w')
json.dump(labels, file, indent=3)
file.close()
