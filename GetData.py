import http.server
from mydatabase import operations
from mypve import pvecommands

print('start')
op = operations()
pve = pvecommands()
op.recordTraffic(pve.fetchListOfVMsInfoDict())
# op.selectInfo("select NETIN,NETOUT from traffic where VMID = 105 and DATE = '2022-01-17'")
rs = op.selectInfo(
    "select VMID,NAME,DATE,DAILYIN,DAILYOUT from traffic where strftime('%Y-%m-%d', datetime('now'),'-2 days') <= strftime('%Y-%m-%d',DATE)")
dicList = {}
for row in rs:
    if row[1] not in dicList :
        dicList[row[1]] = {}
    dicList[row[1]][row[2]] = {'dailyin': row[3], 'dailyout': row[4]}

print(dicList)

option = '''
option = {
  legend: {},
  tooltip: {},
  dataset: {
    dimensions: ['GB', '2015', '2016', '2017'],
    source: [
    ]
  },
  yAxis: { type: 'category' },
  xAxis: {},
series: [ 
    { itemStyle : { normal: {label : {show: true,position: 'right',}}},type: 'bar' }, { itemStyle : { normal: {label : {show: true,position: 'right',}}},type: 'bar' }, { itemStyle : { normal: {label : {show: true,position: 'right',}}},type: 'bar' }]
};
'''

ls = option.split('\n')
dates = []
for value in list(dicList.values()):
    if len(list(value.keys())) >= 3:
        dates = list(value.keys())
        break

for i in range(len(ls)):
    if 'dimensions' in ls[i]:
        ls[i] = ls[i].replace('2015', dates[0]).replace(
            '2016', dates[1]).replace('2017', dates[2])
    elif 'source: [' in ls[i]:
        for k, v in dicList.items():
            for d in dates:
                if d not in v.keys():
                    v[d] = {'dailyin' : 0,'dailyout' : 0}
            string = "{{ GB: '{}', '{}': {}, '{}': {}, '{}': {} }},".format(k, dates[0], v[dates[0]]['dailyout']/(
                1024 * 1024 * 1024), dates[1], v[dates[1]]['dailyout']/(1024 * 1024 * 1024), dates[2], v[dates[2]]['dailyout']/(1024 * 1024 * 1024))
            ls.insert(i+1, string)

cont = ''
with open('index.txt','r') as f:
    cont = f.read()
    cont = cont.replace('placeholder','\n'.join(ls))
    f.close()
with open('index.html','w+') as f:
    f.write(cont)

# httpd = http.server.HTTPServer(
#     ("0.0.0.0", 8000), http.server.SimpleHTTPRequestHandler
# )
# httpd.serve_forever()