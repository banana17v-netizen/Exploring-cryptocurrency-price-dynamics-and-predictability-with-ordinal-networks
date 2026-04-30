import json
with open('08_manuscript.ipynb','r',encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']
print(f'Total cells: {len(cells)}')
full = '\n'.join(''.join(c['source']) for c in cells)

checks = [
    ('[CITE', 'CITE placeholders remaining'),
    ('ARIMA(1,0,0)', 'ARIMA(1,0,0) remaining'),
    ('Table 3.1', 'Table 3.1 remaining'),
    ('Highlights', 'Highlights cell present'),
    ('GARCH(1,1)', 'GARCH(1,1) in Table 4'),
    ('Cross-coin lead-lag', 'Cross-coin section present'),
    ('Data Availability', 'Data Availability Statement present'),
    ('CRediT', 'CRediT statement present'),
    ('Competing Interests', 'Competing Interests present'),
    ('ARIMA(1,0,1)', 'ARIMA(1,0,1) correct name'),
    ('[16]', 'Theiler ref [16] present'),
    ('[17]', 'Kuensch ref [17] present'),
    ('[18]', 'DM ref [18] present'),
]
for pattern, label in checks:
    found = pattern in full
    status = 'OK' if (found and pattern not in ('[CITE','ARIMA(1,0,0)','Table 3.1')) else ('BAD' if found else 'MISSING')
    if pattern in ('[CITE','ARIMA(1,0,0)','Table 3.1'):
        status = 'BAD (still present)' if found else 'OK (removed)'
    print(f'  {status:30s} {label}')

print('\nCell 0 first 300 chars:')
print(''.join(cells[0]['source'])[:300])
