import sqlite3

print('start')
conn = sqlite3.connect("traffic.db")
c = conn.cursor()

cursor = c.execute('select VMID,NAME,DATE,NETIN,NETOUT,DAILYIN,DAILYOUT from traffic')

for row in cursor:
    print(row[0],row[1],row[2],row[5] / (1024.0 * 1024 * 1024),row[6] / (1024.0 * 1024 * 1024))

conn.commit()
conn.close()