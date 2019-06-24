#!/usr/bin/env python
#coding: utf-8
import sys, os
import requests
import json
import re
from lxml import etree
import time

output_file = os.path.dirname(os.path.abspath(__file__)) + '/weather.json'

def fail_exit(msg):
    rt = {}
    rt['error'] = msg
    json.dump(rt, file(output_file, 'w'))
    sys.exit(1)

try:
    r = requests.get('http://weather.sina.com.cn/yantai' \
            , timeout=10)
    r.encoding = 'utf-8'
    html = r.text
except Exception, e:
    fail_exit(unicode(e))

result = {}
result['city_name']       = None
result['current_temp']    = None
result['current_weather'] = None
result['current_wind']    = None
result['current_humidity']= None
result['current_aq']      = None
result['current_aq_desc'] = None
result['days'] = []

tree = etree.HTML(html)
rt = tree.xpath('//*[@id="slider_ct_name"]')
if len(rt):
    result['city_name'] = rt[0].text
rt = tree.xpath('//*[@id="slider_w"]//div[@class="slider_degree"]')
if len(rt):
    result['current_temp'] = rt[0].text.replace(u'℃', '')
rt = tree.xpath('//*[@id="slider_w"]//p[@class="slider_detail"]')
if len(rt):
    tmp0 = re.sub(r'\s', '', rt[0].text)
    tmp0 = tmp0.split('|')
    if len(tmp0) >= 3:
        result['current_weather'] = tmp0[0].strip()
        result['current_wind']    = tmp0[1].strip()
        tmp1 = re.search(r'([\-\d]+)%', tmp0[2])
        if tmp1 is not None:
            result['current_humidity'] = tmp1.group(1)
    tmp0 = None
    tmp1 = None

rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[1]/p')
if len(rt):
    result['current_aq'] = rt[0].text

rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[2]/p[1]')
if len(rt):
    result['current_aq_desc'] = rt[0].text

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div')
for div in rt:
    day = {
            'wind':None,
            'aq':None,
            'aq_desc':None,
            'date':None,
            'weekday':None,
            'day':{
                'weather':None,
                'icon':None,
                'temp':None,
            },
            'night':{
                'weather':None,
                'icon':None,
                'temp':None,
            }
        }

    rt = div.xpath('.//p[contains(@class, "wt_fc_c0_i_date")]')
    if len(rt):
        day['date'] = rt[0].text.strip()

    rt = div.xpath('.//p[contains(@class, "wt_fc_c0_i_day ")]')
    if len(rt):
        day['weekday'] = rt[0].text.strip()

    rt = div.xpath('.//p[contains(@class, "wt_fc_c0_i_icons")]/img')
    if len(rt):
        day['day']['weather'] = rt[0].get('alt')
        day['day']['icon'] = rt[0].get('src')

    if len(rt) > 1:
        day['night']['weather'] = rt[1].get('alt')
        day['night']['icon'] = rt[1].get('src')
    else:
        day['night']['weather'] = day['day']['weather']
        day['night']['icon'] = day['day']['icon']


    rt = div.xpath('.//p[@class="wt_fc_c0_i_temp"]')
    if len(rt):
        tmp0 = rt[0].text.split('/')
        day['day']['temp'] = tmp0[0].replace(u'°C', '').strip()
        if len(tmp0) > 1:
            day['night']['temp'] = tmp0[1].replace(u'°C', '').strip()
        else:
            day['night']['temp'] = day['day']['temp']

    rt = div.xpath('.//p[@class="wt_fc_c0_i_tip"]')
    if len(rt):
        day['wind'] = rt[0].text.strip()

    rt = div.xpath('.//ul[contains(@class, "wt_fc_c0_i_level")]/li')
    if len(rt):
        day['aq'] = rt[0].text.strip()
        day['aq_desc'] = rt[1].text.strip()

    result['days'].append(day)



keys_require = ['city_name', \
    'current_temp', \
    'current_weather', \
    'current_wind', \
    'current_humidity', \
    'current_aq', \
    'current_aq_desc', \
    'days']

for key in keys_require:
    if result.get(key) is None:
       fail_exit('can not get key %s' % key)

result['update'] = int(time.time())
json.dump(result, file(output_file, 'w'), indent=2)
