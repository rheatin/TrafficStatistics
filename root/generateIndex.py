from mydatabase import operations
from mypve import pvecommands

op = operations()
pve = pvecommands()
op.recordTraffic(pve.fetchListOfVMsInfoDict())
rs = op.queryInfo(
    "select VMID,NAME,DATE,DAILYIN,DAILYOUT from traffic")
dicList = {}
for row in rs:
    if row[1] not in dicList :
        dicList[row[1]] = {}
    dicList[row[1]][row[2]] = {'dailyin': row[3], 'dailyout': row[4]}

# {'onething-mechanical': {'2022-03-15': {'dailyin': 124228716481, 'dailyout': 301732080144}, '2022-03-16': {'dailyin': 125592947498, 'dailyout': 321386407870}, '2022-03-17': {'dailyin': 67380184114, 'dailyout': 106208296055}}, 'alpine': {'2022-03-15': {'dailyin': 1537570572, 'dailyout': 1071293151}, '2022-03-16': {'dailyin': 1434803062, 'dailyout': 409136818}, '2022-03-17': {'dailyin': 699149818, 'dailyout': 182700942}}, 'home-assistant': {'2022-03-15': {'dailyin': 963143550, 'dailyout': 211359106}, '2022-03-16': {'dailyin': 490129443, 'dailyout': 211654226}, '2022-03-17': {'dailyin': 183874890, 'dailyout': 79734518}}, 'onething': {'2022-03-15': {'dailyin': 91293289629, 'dailyout': 319740421132}, '2022-03-16': {'dailyin': 105593340787, 'dailyout': 323754319935}, '2022-03-17': {'dailyin': 56067461870, 'dailyout': 70248825930}}, 'openwrt': {'2022-03-15': {'dailyin': 983327572316, 'dailyout': 988761464153}, '2022-03-16': {'dailyin': 1029515775921, 'dailyout': 1035533268051}, '2022-03-17': {'dailyin': 346836705551, 'dailyout': 348267515259}}}
names = list(dicList.keys())
dates = sorted(list(dicList[names[0]].keys()),reverse=True)
print("success")

allEntities = []
for name in names:
    data = []
    alldayData = dicList[name]
    for date in dates:
        if not date in alldayData.keys():
            data.append(0);
        else:
            data.append(round(alldayData[date]["dailyout"]/(1024.0 * 1024.0 * 1024.0),2))
    anEntity = {"name": name,"type": 'bar',"barGap": 0,"label": "labelOption","emphasis": {"focus": 'series'},"data": data}
    allEntities.append(anEntity)
series = allEntities

labels = []
for _ in names:
    labels.append({'label': 'labelOption'})

with open("mainTemplate.html","r") as f:
    jsContent = f.read()
    jsContent = jsContent.replace("LABELS",str(labels).replace("'labelOption'","labelOption"))
    jsContent = jsContent.replace("NAMES",str(names))
    jsContent = jsContent.replace("DATES",str(dates))
    jsContent = jsContent.replace("SERIES",str(series).replace("'labelOption'","labelOption"))
    f.close()
    with open("index.html","w+") as fw:
        fw.write(jsContent)
        fw.close()
