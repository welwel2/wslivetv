# This scrip will commit the latest changes, and then, push the changes to 
# remote server.
# Call the cr script to update the wsrepo on remote server.
import sys
import os

crn = r'C:\Users\220554\Documents\GitHub\wsrepo\_tools\cr.py'

sys.path.append(os.path.split(crn)[0])
print sys.path
from cr import update_remote

update_remote(os.getcwd(), 'ltv')

os.system(r'python %s'%crn)

