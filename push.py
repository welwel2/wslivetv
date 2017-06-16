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

print "issue git command to add modified files"
os.system(r'git add *')

print "issue git command to commit changes"
comment = raw_input('enter a good description for your changes: ')
os.system(r'git commit -m "%s"'%comment)
#update_remote(os.getcwd(), 'ltv')

print "issue git command to push changes to server"
os.system(r'git push')

print "issue git command to print status"
os.system(r'git status')

print "issue git command to display log"
os.system(r'git log --oneline')

print "call script to update wsrepo repository on github server"
#os.system(r'python %s'%crn)

