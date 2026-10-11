import sys

TEMPLATE = r'C:\Users\AL-BATRIQ\AppData\Local\hermes\cache\scratch\dashboard_template_mp.html'
LIB      = r'C:\Users\AL-BATRIQ\AppData\Local\hermes\cache\scratch\echarts.min.js'
OUT      = r'C:\Users\AL-BATRIQ\Downloads\m\Sales_Dashboard_2022-2025.html'

# ---- Step 1: substitute the data placeholders into the template ----
# (Mirrors build_dashboard_v2.py's replacements; that script produced the
#  correct HTML, we just re-derive it here so the pipeline is one pass.)
import pandas as pd, json
from datetime import datetime

df = pd.read_csv(r'C:\Users\AL-BATRIQ\Downloads\m\Sales_transactions_2022-2025.csv')
raw_count = len(df)
dups = int(df['Transaction_ID'].duplicated().sum())
df = df.drop_duplicates(subset='Transaction_ID', keep='first')
gender_map = {'male':'Male','Male':'Male','FEMALE':'Female','Female':'Female','Non-binary':'Non-binary','Non Binary':'Non-binary'}
df['Customer_Gender'] = df['Customer_Gender'].map(gender_map)
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Year'] = df['Order_Date'].dt.year; df['Month'] = df['Order_Date'].dt.month
df['DayOfWeek'] = df['Order_Date'].dt.day_name()
df['Hour'] = pd.to_datetime(df['Order_Time'], format='%H:%M:%S').dt.hour
missing_age = int(df['Customer_Age'].isna().sum())
df['Customer_Age'] = df['Customer_Age'].fillna(df['Customer_Age'].median())
missing_gender = int(df['Customer_Gender'].isna().sum())
df['Customer_Gender'] = df['Customer_Gender'].fillna('Unknown')
# Merge Non-binary and Unknown into Female (user request)
df['Customer_Gender'] = df['Customer_Gender'].replace('Non-binary', 'Unknown')
df['Customer_Gender'] = df['Customer_Gender'].replace('Unknown', 'Female')
missing_name = int(df['Customer_Name'].isna().sum())
df['Customer_Name'] = df['Customer_Name'].fillna('Anonymous')
df.loc[df['Customer_Age'] < 18, 'Customer_Age'] = 18
df.loc[df['Customer_Age'] > 100, 'Customer_Age'] = 100
AGE_LABELS = ['18-25','26-35','36-45','46-55','56-65','66+']
df['Age_Group'] = pd.cut(df['Customer_Age'], bins=[0,25,35,45,55,65,100], labels=AGE_LABELS)
df = df.sort_values('Order_Date').reset_index(drop=True)
clean_count = len(df)

# One row per Customer_ID (names already imputed above, so no NaN/real split creates dupes)
customers = (df[['Customer_ID','Customer_Name']]
               .groupby('Customer_ID', as_index=False)['Customer_Name'].first()
               .sort_values('Customer_ID'))
assert customers['Customer_ID'].nunique() == len(customers), 'customer list still has duplicate IDs'
cust_map = {c:i for i,c in enumerate(customers['Customer_ID'])}
cust_list = [[str(r.Customer_ID), str(r.Customer_Name)] for r in customers.itertuples()]
order_ids = df['Order_ID'].unique(); order_map = {o:i for i,o in enumerate(order_ids)}
YEARS = sorted(df['Year'].unique().tolist())
meta = {'years':YEARS,
        'channels':['Online','Retail Store','B2B Portal','Phone Order'],
        'segments':['Consumer','Small Business','Returning Customer','Corporate','New Customer','Premium'],
        'genders':['Female','Male'],
        'ageGroups':AGE_LABELS,
        'dows':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']}
yi={y:i for i,y in enumerate(YEARS)}; ci={c:i for i,c in enumerate(meta['channels'])}
si={s:i for i,s in enumerate(meta['segments'])}; gi={g:i for i,g in enumerate(meta['genders'])}
ai={a:i for i,a in enumerate(AGE_LABELS)}; di={d:i for i,d in enumerate(meta['dows'])}
rows=[]
for r in df.itertuples():
    rows.append([cust_map[r.Customer_ID], order_map[r.Order_ID], yi[r.Year], r.Month-1,
                 di[r.DayOfWeek], r.Hour, ci[r.Sales_Channel], si[r.Customer_Segment],
                 gi[r.Customer_Gender], ai[r.Age_Group], int(r.Customer_Age)])
DATA_JSON = json.dumps(rows, separators=(',',':')); META_JSON = json.dumps(meta)
CUST_JSON = json.dumps(cust_list, separators=(',',':')); NORDERS = len(order_ids)

ch=df['Sales_Channel'].value_counts(); sg=df['Customer_Segment'].value_counts()
gn=df['Customer_Gender'].value_counts(); ag=df['Age_Group'].value_counts()
S={'total':clean_count,'raw':raw_count,'dups':dups,'norders':NORDERS,
   'missing':{'age':missing_age,'gender':missing_gender,'name':missing_name},
   'unique_customers':int(df['Customer_ID'].nunique()),
   'avg_age':round(float(df['Customer_Age'].mean()),1),
   'median_age':round(float(df['Customer_Age'].median()),1),
   'corr':round(float(df['Customer_Age'].corr(df['Hour'])),3),
   'cleaning_log':[f"Removed {dups} duplicate Transaction_ID rows"],
   'ch':{k:int(v) for k,v in ch.items()},'seg':{k:int(v) for k,v in sg.items()},
   'gen':{k:int(v) for k,v in gn.items()},'ag':{str(k):int(v) for k,v in ag.items()},
   'ch_pct':{k:round(v/clean_count*100,1) for k,v in ch.items()},
   'seg_pct':{k:round(v/clean_count*100,1) for k,v in sg.items()},
   'gen_pct':{k:round(v/clean_count*100,1) for k,v in gn.items()},
   'yearly':{str(k):int(v) for k,v in df.groupby('Year').size().items()},
   'peak_hour':f"{int(df.groupby('Hour').size().idxmax()):02d}:00",
   'peak_dow':df['DayOfWeek'].value_counts().idxmax(),
   'yoy':round((df.groupby('Year').size().iloc[-1]/df.groupby('Year').size().iloc[0]-1)*100,1),
   'date_range':f"{df['Order_Date'].min().strftime('%b %Y')} to {df['Order_Date'].max().strftime('%b %Y')}",
   'top_age_group':str(ag.idxmax())}
S_JSON = json.dumps(S)

with open(TEMPLATE, encoding='utf-8') as f:
    html = f.read()
html = (html.replace('__DATA_JSON__', DATA_JSON).replace('__META_JSON__', META_JSON)
            .replace('__CUST_JSON__', CUST_JSON).replace('__S_JSON__', S_JSON)
            .replace('__NORDERS__', str(NORDERS)).replace('__NCUST__', str(len(cust_list)))
            .replace('__DR__', S['date_range']).replace('__TOTAL__', f"{clean_count:,}")
            .replace('__RAW__', f"{raw_count:,}").replace('__DUPS__', str(dups))
            .replace('__GEN_DATE__', datetime.now().strftime('%B %d, %Y at %H:%M')))

assert '__DATA_JSON__' not in html, 'placeholder substitution failed'

# ---- Step 2: inline the ECharts library (no CDN needed) ----
with open(LIB, encoding='utf-8') as f:
    lib = f.read()
assert '</script' not in lib.lower(), 'library contains a closing script tag'
cdn = '<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>'
assert cdn in html
html = html.replace(cdn, '<script>\n' + lib + '\n</script>')

# ---- Step 3: drop the Google Fonts @import so it works fully offline ----
font_line = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');"
if font_line in html:
    html = html.replace(font_line + '\n', '')
    print('removed Google Fonts @import (offline-safe fallback fonts now apply)')

# ---- Step 4: defensive guard before </body> (never splits a const decl) ----
guard = '''<script>
(function(){
  if (typeof echarts === 'undefined') {
    var b = document.createElement('div');
    b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#ef4444;color:#fff;padding:14px 20px;font:600 14px Inter,sans-serif;text-align:center';
    b.textContent = 'Chart engine failed to load. Use a modern browser (Chrome/Edge/Firefox) with JavaScript enabled.';
    document.body.prepend(b); return;
  }
})();
</script>
</body>'''
assert '\n</body>' in html
html = html.replace('\n</body>', '\n' + guard, 1)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

# ---- Self-check on the written file ----
with open(OUT, encoding='utf-8') as f:
    final = f.read()
import json as _json, re as _re
_m = _re.search(r'const CUST = (\[\[.*?\]\]);', final, _re.S)
_c = _json.loads(_m.group(1)) if _m else []
_cids = [x[0] for x in _c]
checks = {
  'no __DATA_JSON__ placeholder': '__DATA_JSON__' not in final,
  'echarts inlined': 'echarts.init' in final and 'Apache Software Foundation' in final,
  'no CDN refs': 'cdn.jsdelivr.net' not in final,
  'no Google Fonts': 'fonts.googleapis.com' not in final,
  'DATA array non-empty': 'const DATA = [[' in final,
  'row count sane': final.count('],[', final.find('const DATA'), final.find('const DATA')+600000) > 17000,
  'customer list unique IDs (no dupes)': len(_cids) == len(set(_cids)) and len(_cids) == len(cust_list),
  'customer count matches CSV': len(cust_list) == S['unique_customers'],
}
for k,v in checks.items():
    print(('PASS ' if v else 'FAIL ') + k)
assert all(checks.values()), 'self-check failed'
print(f'\nOK: self-contained dashboard {len(final)/1024/1024:.2f} MB, {clean_count:,} rows, {NORDERS:,} orders')
