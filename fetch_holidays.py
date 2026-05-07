import urllib.request
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

API_KEY = os.environ.get('API_KEY', '')
BASE_URL = 'https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'

def fetch_month(year, month):
    mm = str(month).zfill(2)
    url = f'{BASE_URL}?serviceKey={API_KEY}&solYear={year}&solMonth={mm}&numOfRows=20'
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            xml_data = res.read().decode('utf-8')
        root = ET.fromstring(xml_data)
        EXCLUDE = {
            '어버이날', '스승의날', '납세자의 날', '소비자의 날',
            '방재의 날', '환경의 날', '정보통신의 날',
            '육군의 날', '해군의 날', '공군의 날',
        }
        dates = []
        for item in root.findall('.//item'):
            is_holiday = item.findtext('isHoliday', '')
            locdate = item.findtext('locdate', '')
            datename = item.findtext('dateName', '').strip()
            if not locdate or not datename:
                continue
            if datename in EXCLUDE:
                continue
            # isHoliday=Y 이거나, 이름이 있는 공휴일 항목 포함
            # 토/일 겹치는 공휴일은 isHoliday=N으로 오는 경우 있음
            if is_holiday == 'Y' or datename:
                s = str(locdate)
                if len(s) == 8:
                    dates.append(f'{s[0:4]}-{s[4:6]}-{s[6:8]}')
        return dates
    except Exception as e:
        print(f'  Error {year}/{mm}: {e}')
        return []

def fetch_year(year):
    all_dates = []
    for month in range(1, 13):
        dates = fetch_month(year, month)
        print(f'  {year}/{month:02d}: {dates}')
        all_dates.extend(dates)
    return sorted(set(all_dates))

current_year = datetime.now().year
next_year = current_year + 1

print(f'Fetching {current_year}...')
cur_dates = fetch_year(current_year)
print(f'Fetching {next_year}...')
next_dates = fetch_year(next_year)

data = {
    str(current_year): cur_dates,
    str(next_year): next_dates,
    'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
}

with open('holidays.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done:', json.dumps(data, ensure_ascii=False))
