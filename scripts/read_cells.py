import json
with open('08_manuscript.ipynb','r',encoding='utf-8') as f:
    nb = json.load(f)
for i in [0,1,4,5]:
    print(f'=== CELL {i} ===')
    print(''.join(nb['cells'][i]['source']))
    print()
