import requests
 
# Making a P
# UT request
myfiles = {'file': open('address.png' ,'rb')}
r = requests.put('http://localhost:3000/api/image_bombbot', auth=("notebook_regi", "48865012-47a6-4a31-b082-af84e7150988"), files = myfiles)
 
# check status code for response received
# success code - 200
print(r)
 
# print content 
# of request
print(r.content)