# This scrip will commit the latest changes, and then, push the changes to 
# remote server.
# Call the cr script to update the wsrepo on remote server.
import sys
import os

crn = r'C:\Users\220554\Documents\GitHub\wsrepo\_tools\cr.py'

sys.path.append(os.path.split(crn)[0])
#print sys.path
from cr import update_remote

print "call script to clean directory"
os.system(r'python clean.py')

print "issue git command to remove unwated files"
os.system(r'git rm *.py[oc]')

print "call update_remote to commit changes, and push to server"
update_remote(os.getcwd(), 'ltv')

print "call script to update wsrepo repository on github server"
#os.system(r'python %s'%crn)

