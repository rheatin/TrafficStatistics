from mimetypes import init
import sqlite3
import time
from datetime import date, timedelta


class operations(object):
    def __init__(self, dbPath='traffic.db'):
        self.conn = sqlite3.connect(dbPath)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def recordTraffic(self,dictsList):
        for tmp in dictsList:
            vmid = tmp["vmid"]
            netin = tmp["netin"]
            netout = tmp["netout"]
            name = tmp["name"]

            command = """
                CREATE TABLE IF NOT EXISTS traffic
                        (VMID INTEGER,
                        DATE TEXT,
                        NAME TEXT,
                        NETIN INTEGER,
                        NETOUT INTEGER,
                        DAILYIN INTEGER,
                        DAILYOUT INTEGER, 
                        RAW TEXT,
                        PRIMARY KEY(VMID,DATE));
                """
            self.cursor.execute(command)

            command = "select NETIN,NETOUT from traffic where strftime('%Y-%m-%d', datetime('now'),'-1 days') = strftime('%Y-%m-%d',DATE) and VMID = {}".format(
                str(vmid)
            )

            dailyin = 0
            dailyout = 0

            cursor = self.cursor.execute(command)
            rs = cursor.fetchone()
            if rs:
                netinOfYesterday = rs[0]
                netoutOfYesterday = rs[1]
                dailyin = netin - int(netinOfYesterday)
                dailyout = netout - int(netoutOfYesterday)

            else:
                # INSERT FAKE NETIN AND NETOUT FOR YESTERDAY TO CALCULATE THE DAILYIN AND DAILYOUT
                yesterday = (date.today() + timedelta(days=-1)
                             ).strftime("%Y-%m-%d")
                command = 'INSERT INTO traffic (VMID,DATE,NAME,NETIN,NETOUT,DAILYIN,DAILYOUT,RAW) \
                    VALUES ({},"{}","{}",{},{},{},{},"{}")'.format(
                    str(vmid),
                    yesterday,
                    str(name),
                    str(netin),
                    str(netout),
                    str(dailyin),
                    str(dailyout),
                    "FAKE",
                )
                self.cursor.execute(command)

            print(
                time.asctime(time.localtime(time.time())), ",",
                vmid, ",",
                time.strftime("%Y-%m-%d", time.localtime()), ",",
                netin, ",",
                netout, ",",
                dailyin, ",",
                dailyout,
            )
            command = 'REPLACE INTO traffic (VMID,DATE,NAME,NETIN,NETOUT,DAILYIN,DAILYOUT,RAW) \
                    VALUES ({},"{}","{}",{},{},{},{},"{}")'.format(
                str(vmid),
                time.strftime("%Y-%m-%d", time.localtime()),
                str(name),
                str(netin),
                str(netout),
                str(dailyin),
                str(dailyout),
                str(tmp),
            )
            self.cursor.execute(command)
            self.conn.commit()

    def selectInfo(self,stmt):
        cursor = self.cursor.execute(stmt)
        rs = cursor.fetchall()
        self.conn.commit()
        return rs