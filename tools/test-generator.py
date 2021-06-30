#!/usr/bin/python

import sys
import math
import urllib.parse
import http.client
import time
import random

id = '123456789012345'
server = 'localhost:5055'
period = 1
step = 0.001
device_speed = 40
driver_id = '123456'

waypoints = [
(37.70406996979375, 48.97943184110548),
(37.70432462259622, 48.98013457975377),
(37.704120900424215, 48.980156037425516),
(37.704256715267775, 48.980510089009194),
(37.70432462259622, 48.98083195408526),
(37.704384041457566, 48.98079976757765),
(37.7042142731559, 48.9809928866233),
(37.704384041457566, 48.98072466572657),
(37.7043585762371, 48.98126110752003),
(37.70440950666928, 48.98151859958088),
(37.70447741385776, 48.981464955401535),
(37.704417995071246, 48.98181900698521),
(37.704434971872246, 48.98209795671781),
(37.70446043706645, 48.98245200830149),
(37.70462171642666, 48.982655856183015),
(37.704587762906314, 48.98295626358734),
(37.704468925462585, 48.98274168686996),
(37.704604739668405, 48.98298845009494),
(37.70471508852742, 48.98311719612538),
(37.704545320984, 48.98304209427429)
]

points = []

for i in range(0, len(waypoints)):
    (lat1, lon1) = waypoints[i]
    (lat2, lon2) = waypoints[(i + 1) % len(waypoints)]
    length = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)
    count = int(math.ceil(length / step))
    for j in range(0, count):
        lat = lat1 + (lat2 - lat1) * j / count
        lon = lon1 + (lon2 - lon1) * j / count
        points.append((lat, lon))

def send(conn, lat, lon, course, speed, alarm, ignition, accuracy, rpm, fuel, driverUniqueId):
    params = (('id', id), ('timestamp', int(time.time())), ('lat', lat), ('lon', lon), ('bearing', course), ('speed', speed))
    if alarm:
        params = params + (('alarm', 'sos'),)
    if ignition:
        params = params + (('ignition', 'true'),)
    if accuracy:
        params = params + (('accuracy', accuracy),)
    if rpm:
        params = params + (('rpm', rpm),)
    if fuel:
        params = params + (('fuel', fuel),)
    if driverUniqueId:
        params = params + (('driverUniqueId', driverUniqueId),)
    conn.request('GET', '?' + urllib.parse.urlencode(params))
    conn.getresponse().read()

def course(lat1, lon1, lat2, lon2):
    lat1 = lat1 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    return (math.atan2(y, x) % (2 * math.pi)) * 180 / math.pi

index = 0

conn = http.client.HTTPConnection(server)

while True:
    (lat1, lon1) = points[index % len(points)]
    (lat2, lon2) = points[(index + 1) % len(points)]
    speed = device_speed if (index % len(points)) != 0 else 0
    alarm = (index % 10) == 0
    ignition = (index % len(points)) != 0
    accuracy = 100 if (index % 10) == 0 else 0
    rpm = random.randint(500, 4000)
    fuel = random.randint(0, 80)
    driverUniqueId = driver_id if (index % len(points)) == 0 else False
    send(conn, lat1, lon1, course(lat1, lon1, lat2, lon2), speed, alarm, ignition, accuracy, rpm, fuel, driverUniqueId)
    time.sleep(period)
    index += 1
