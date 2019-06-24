#!/usr/bin/env python
#encoding: utf-8
import sys
import os
import time
import datetime
import json
import requests
import re
import struct
from StringIO import StringIO
from PIL import Image, ImageDraw, ImageFont

color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_red = (227, 178, 4)

image_width = 640
image_height = 384

font_path = os.path.dirname(os.path.abspath(__file__)) + '/font.ttc'

def current_datetime():
    m = ['一', '二', '三', '四', '五', '六', '日']
    n = datetime.datetime.now()
    return (n.strftime('%m-%d %H:%M 星期') + m[n.weekday()]).decode('utf-8')

def fetch_finance():
    url = 'https://hq.sinajs.cn/rn=%d&list=gb_dji,gb_ixic,gb_inx,s_sh000001,s_sz399001,USDCNY' % int(time.time())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    text = r.text
    matches = re.findall(r'var ([^=]+)="([^"]+)"', text, re.M)

    result = {}
    for v in matches:
        result[v[0]] = v[1].split(',')

    return result

def draw_finance(draw, item, pos):
    font = ImageFont.truetype(font_path, 20)

    left = pos[0]
    top = pos[1] + 10
    text = item[0]
    draw.text((left, top), text, font=font, fill=color_black)
    w, h = draw.textsize(text, font=font)
    w2, h2 = draw.textsize(u'四个字符', font=font)
    if w < w2:
        w = w2

    left += w + 10
    text = u'%.2f' % item[1]
    w, h = draw.textsize(text, font=font)
    draw.text((left, top), text, font=font, fill=color_black)

    bg_color = None
    txt_color = None
    left += w + 10

    if item[2] > 0:
        bg_color = color_red
        txt_color = color_black
        text = u'+%.2f%%' % item[2]
    else:
        bg_color = color_black
        txt_color = color_white
        text = u'-%f%' % item[2]

    w, h = draw.textsize(text, font=font)
    draw.rectangle([left-2, top-2, left + w + 2, top + h + 2], fill=bg_color)
    draw.text((left, top), text, font=font, fill=txt_color)

def load_icon(url):
    r = requests.get(url)
    png = Image.open(StringIO(r.content))
    background = Image.new("RGB", png.size, (255, 255, 255))
    background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
    return background

def draw_weather(image, draw, day, pos, width):
    is_today = datetime.datetime.now().strftime('%m-%d') == day['date']

    font = ImageFont.truetype(font_path, 24)

    left = pos[0]
    top = pos[1] + 10
    text = day['date']
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2 + left, top), text, font=font, fill=color_black)

    top += h + 5
    text = day['weekday']
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2 + left, top), text, font=font, fill=color_black)

    top += h + 5
    if is_today:
        icon = load_icon(day['day']['icon'])
        icon_margin = (width - icon.size[0])/2
        image.paste(icon, (icon_margin + left, top))
    else:
        icon = load_icon(day['day']['icon'])
        icon_margin = width/2 - icon.size[0] - 10
        image.paste(icon, (icon_margin + left, top))

        icon = load_icon(day['night']['icon'])
        image.paste(icon, (left + width/2 + 10, top))

    font = ImageFont.truetype(font_path, 20)
    text = day['day']['temp'] + u'℃'
    if not is_today:
        text += ' / ' + day['night']['temp'] + u'℃'
    top += h + 30
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2 + left, top), text, font=font, fill=color_black)

    font = ImageFont.truetype(font_path, 16)
    text = day['wind']
    top += h + 5
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2 + left, top), text, font=font, fill=color_black)

    font = ImageFont.truetype(font_path, 24)
    text = day['aq'] + u' ' + day['aq_desc']
    top += h + 5
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2 + left, top), text, font=font, fill=color_black)


def draw_board():
    image = Image.new('RGB', (image_width, image_height), color_white)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, 60)

    line = current_datetime()
    w, h = draw.textsize(line, font=font)
    draw.text(((image_width-w)/2,10), line, font=font, fill=color_black)

    draw.line([(0, 80),(image_width, 80)], fill=color_black, width=1)

    json_path = os.path.dirname(os.path.abspath(__file__)) + '/weather.json'
    weather_info = json.load(open(json_path))
    weather_info['days'][0]['day']['temp'] = weather_info['current_temp']
    weather_info['days'][0]['wind'] = weather_info['current_wind']
    weather_info['days'][0]['aq'] = weather_info['current_aq']
    weather_info['days'][0]['aq_desc'] = weather_info['current_aq_desc']

    for i in xrange(4):
        width = image_width / 4
        draw_weather(image, draw, weather_info['days'][i], (0 + i * width, 80), width)
        if i != 3:
            draw.line([((i+1)*width, 80),((i+1)*width, 80+200)], fill=color_black, width=1)

    draw.line([(0, 80+200),(image_width, 80+200)], fill=color_black, width=1)

    finance = fetch_finance()
    draw_finance(draw, (u'道琼斯', float(finance['hq_str_gb_dji'][1]), float(finance['hq_str_gb_dji'][2])), (20, 280))
    draw_finance(draw, (u'纳斯达克', float(finance['hq_str_gb_ixic'][1]), float(finance['hq_str_gb_ixic'][2])), (image_width/2, 280))

    draw_finance(draw, (u'上证指数', float(finance['hq_str_s_sh000001'][1]), float(finance['hq_str_s_sh000001'][3])), (20, 310))
    draw_finance(draw, (u'深证成指', float(finance['hq_str_s_sz399001'][1]), float(finance['hq_str_s_sz399001'][3])), (image_width/2, 310))

    c = float(finance['hq_str_USDCNY'][8])
    o = float(finance['hq_str_USDCNY'][3])
    draw_finance(draw, (u'美元兑人民币', c, (c-o)/o*100), (20, 340))

    return image

def convert_image(im, output_path):
    output_fp = open(output_path, "w")

    w, h = im.size
    size = w*h

    i = 0
    while i < size:
        b = 0x00

        for j in xrange(4):
            idx = i + j
            if idx < size:
                px = im.getpixel((idx%w, idx/w))
                if px[0] > 230 and px[1] > 230 and px[2] > 230: #white
                    b |= 0x01 << ((3 - j)*2)
                elif px[0] > 200:
                    b |= 0x02 << ((3 - j)*2)
            else:
                break

        output_fp.write(struct.pack("B", b))

        i += 4



if __name__ == '__main__':
    image = draw_board()
    #image.save("./board.bmp")
    convert_image(image, sys.argv[1])
