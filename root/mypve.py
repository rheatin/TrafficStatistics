import os
import threading
import yaml

class pvecommands():
    def __init__(self) -> None:
        self.dictsList = []

    def readVMInfo(self, vmInfo):
        cmd = "qm status " + vmInfo["VMID"] + " --verbose"
        p = os.popen(cmd)
        tmp = p.read()
        tmp = yaml.safe_load(tmp.replace("\t", "    "))
        p.close()
        self.dictsList.append(tmp)
    
    def fetchAllVMs(self):
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
        return vmInfos

    def fetchListOfVMsInfoDict(self):
        threads = []
        for vmInfo in self.fetchAllVMs():
            t = threading.Thread(target=self.readVMInfo, args=(vmInfo,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return self.dictsList