from http.client import HTTPConnection

# TODO read from config
# TODO HTTPs support

c = HTTPConnection("localhost", 8080)
c.request("POST", "/process", "{}")
doc = c.getresponse().read()

print(doc)