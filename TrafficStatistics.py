#cron 59 23 * * *

from concurrent.futures import thread
import threading
from mydatabase import operations
from mypve import pvecommands

times = 20

def startRecording():
    global times
    if times > 0:
        op = operations()
        pve = pvecommands()

        # 101,onething,2022-01-18,2542608095173,7000098385919,53367164064,71000199441
        # fakeList = [{'vmid':101,'name':'onething','netin':2542608095173,'netout':7000098385919}]
        # op.recordTraffic(fakeList)
        op.recordTraffic(pve.fetchListOfVMsInfoDict())
        times = times - 1
        threading.Timer(3, startRecording).start()

if __name__ == '__main__':
    startRecording()
