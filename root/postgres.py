import psycopg2
import datetime
import time

class postgres(object):
    def __init__(self, database="postgres",user="postgres",password="991788",host="192.168.1.20",port="54320"):
        self.conn = psycopg2.connect(database=database,user=user,password=password,host=host,port=port)
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
                        (VMID bigint,
                        DATE date,
                        NAME name,
                        NETIN bigint,
                        NETOUT bigint,
                        DAILYIN bigint,
                        DAILYOUT bigint, 
                        RAW TEXT,
                        PRIMARY KEY(VMID,DATE));
                """
            self.cursor.execute(command)

            command = "select NETIN,NETOUT from traffic where DATE = 'yesterday' and VMID = {}".format(
                str(vmid)
            )

            dailyin = 0
            dailyout = 0

            self.cursor.execute(command)
            rs = self.cursor.fetchone()
            if rs:
                netinOfYesterday = rs[0]
                netoutOfYesterday = rs[1]
                dailyin = netin - int(netinOfYesterday)
                dailyout = netout - int(netoutOfYesterday)

            else:
                # INSERT FAKE NETIN AND NETOUT FOR YESTERDAY TO CALCULATE THE DAILYIN AND DAILYOUT
                yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)
                             ).strftime("%Y-%m-%d")
                command = "INSERT INTO traffic (VMID,DATE,NAME,NETIN,NETOUT,DAILYIN,DAILYOUT,RAW) \
                    VALUES ({},'{}','{}',{},{},{},{},'{}')".format(
                    vmid,
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
            command = '''INSERT INTO traffic (VMID,DATE,NAME,NETIN,NETOUT,DAILYIN,DAILYOUT,RAW) \
        VALUES({},'{}','{}',{},{},{},{},'{}') \
ON CONFLICT (VMID,DATE) \
DO UPDATE SET \
    NAME = EXCLUDED.name,NETIN=EXCLUDED.netin,NETOUT=EXCLUDED.netout,DAILYIN=EXCLUDED.dailyin,DAILYOUT=EXCLUDED.dailyout,RAW=EXCLUDED.raw'''.format(
                vmid,
                time.strftime("%Y-%m-%d", time.localtime()),
                str(name),
                str(netin),
                str(netout),
                str(dailyin),
                str(dailyout),
                str(tmp).replace("\'","\""),
            )
            self.cursor.execute(command)
            self.conn.commit()

    def queryInfo(self,stmt):
        if(stmt.startswith("select")):
            self.cursor.execute(stmt)
            rs = self.cursor.fetchall()
            self.conn.commit()
            return rs
        else:
            self.cursor.execute(stmt)
            self.conn.commit()
            return self.cursor.rowcount
