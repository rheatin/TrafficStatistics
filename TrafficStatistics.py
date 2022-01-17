from concurrent.futures import thread
import os
import yaml
import sqlite3
import time
import threading
from datetime import date, timedelta


dictsList = []
def readVMInfo(vmInfo):
    cmd = "qm status " + vmInfo["VMID"] + " --verbose"
    p = os.popen(cmd)
    tmp = p.read()
    tmp = yaml.safe_load(tmp.replace("\t", "    "))
    p.close()
    dictsList.append(tmp)
    


def recordTraffic():

    p = os.popen("qm list")
    vmListRaw = p.read()
    p.close()

    # with open("tmp.txt","r") as f:
    #     vmListRaw = f.read()
    """ 
        VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID       
        100 openwrt              running    1024               0.00 4027452   
        101 onething             running    10240            238.47 685861    
        102 onething-mechanical  running    8192            1024.00 372718    
        104 home-assistant       running    1536              32.00 1475      
        105 alpine               running    10240            200.00 1831833   
    """
    vmInfosRaw = vmListRaw.split("\n")
    columns = []
    vmInfos = []
    for vmInfoRawString in vmInfosRaw:
        if vmInfoRawString == "":
            continue
        #       100 openwrt              running    1024               0.00 4027452
        vmInfoList = vmInfoRawString.split(" ")
        while "" in vmInfoList:
            vmInfoList.remove("")
        if "VMID" in vmInfoList:
            columns = vmInfoList
        else:
            vmInfo = {}
            for i in range(len(vmInfoList)):
                vmInfo[columns[i]] = vmInfoList[i]
            vmInfos.append(vmInfo)

    conn = sqlite3.connect("traffic.db")

    threads = []
    
    for vmInfo in vmInfos:
        c = conn.cursor()
        t = threading.Thread(target=readVMInfo,args=(vmInfo,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

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
        c.execute(command)

        command = "select NETIN,NETOUT from traffic where strftime('%Y-%m-%d', datetime('now'),'-1 days') = strftime('%Y-%m-%d',DATE) and VMID = {}".format(
            str(vmid)
        )

        dailyin = 0
        dailyout = 0

        cursor = c.execute(command)
        rs = cursor.fetchone()
        if rs:
            netinOfYesterday = rs[0]
            netoutOfYesterday = rs[1]
            dailyin = netin - int(netinOfYesterday)
            dailyout = netout - int(netoutOfYesterday)

        else:
            # INSERT FAKE NETIN AND NETOUT FOR YESTERDAY TO CALCULATE THE DAILYIN AND DAILYOUT
            yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
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
            c.execute(command)

        print(
            vmid,
            time.strftime("%Y-%m-%d", time.localtime()),
            netin,
            netout,
            dailyin,
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
        c.execute(command)
        conn.commit()


def startRecording():
    recordTraffic()
    threading.Timer(10, startRecording).start()


startRecording()
