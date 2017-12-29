import os
import glob

wslivetv_p = r'C:\Users\220554\AppData\Roaming\Kodi\addons\plugin.video.wslivetv'
for (dirname, subshere, fileshere) in os.walk(wslivetv_p):
    tempf = glob.glob('%s\*.py[co]'%dirname)
    if '.git' in dirname: continue
    if tempf: 
        for filen in tempf:
            print ('deleting %s'%filen)
            os.remove(filen)
