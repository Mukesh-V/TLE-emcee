from skyfield.api import EarthSatellite, load
import os
import json
import csv
import time

directory = './data/'
ts = load.timescale()
timesteps = 100

file = open('labels.json', 'r')
data = json.load(file)
file.close()

try:
    os.mkdir(directory)
except:
    print('Directory found :)')

satellites = []
for i in data:
    satellites.append( EarthSatellite(i['line1'],i['line2'], name=i['name']) )
by_name = {sat.name:sat for sat in satellites}
print(len(satellites), 'satellites loaded!')

for i in range(timesteps):
    for sat in satellites:
        try:
            r = open('./data/' + sat.name + '.csv', 'r')
            reader = csv.reader(r)
            count = len(list(reader))
            if count >= timesteps:
                satellites.remove(by_name[sat.name])
                continue
            r.close()
        except:
            pass
            
        with open('./data/' + sat.name + '.csv', 'a') as f:
            t = ts.now()
            writer = csv.writer(f)
            pos = sat.at(t).position.km
            vel = sat.at(t).velocity.km_per_s
            timestamp = int( ts.now().utc_datetime().timestamp() )
            writer.writerow([timestamp, pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]])
            
    time.sleep(10)    
    print('Timestep :', i)