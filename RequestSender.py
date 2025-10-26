import requests
import models.Clients as cl
import json

class RequestSender:
  baseUrl = "http://localhost:8080"

  def __init__(self, lambda_req : float = 3):
    self.lambda_req = lambda_req

  def sendRequest(self, client_id : str):
    body = { "client_id": client_id }
    json_payload = json.dumps(body)
    print(f"json_payload -> {json_payload}")
    url = f"{self.baseUrl}/process"
    print(f"here's faking url: {url}")
    r = requests.post(url, data = json_payload)

    print(f"status code -> {r.status_code}")

    if r.status_code == 200:
      print(r.json())
    else:
      print("error")

request_sender = RequestSender(3)
print("sending request...")
request_sender.sendRequest(client_id = str(cl.Clients.CLIENT_ONE.value[0]))
