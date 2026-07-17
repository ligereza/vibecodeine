import urllib.request, urllib.parse, json, time

data = urllib.parse.urlencode({"tema": "test1", "modo": "research", "n": "1"}).encode()
req = urllib.request.Request("http://127.0.0.1:8890/run", data=data)
urllib.request.urlopen(req)

for _ in range(10):
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8890/status")
        print("STATUS:", resp.read().decode())
    except Exception as e:
        print("ERR:", e)
    time.sleep(2)
