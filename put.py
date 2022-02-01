import requests

url = "http://192.168.64.1:3000/api/bcoin_image"

payload={}
files=[
  ('multipleFiles',('cmd.png',open('address.png','rb'),'image/png'))
]
headers = {
  'Authorization': 'Basic bm90ZWJvb2tfcmVnaTo0ODg2NTAxMi00N2E2LTRhMzEtYjA4Mi1hZjg0ZTcxNTA5ODg='
}

response = requests.request("PUT", url, headers=headers, data=payload, files=files)

print(response.text)