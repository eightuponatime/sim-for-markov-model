import RequestSender
from models import Clients as cl_model
import random

if __name__ == "__main__":
  pass

request_sender = RequestSender.RequestSender(3)

cl_list = [
  cl_model.Clients.CLIENT_ONE,
  cl_model.Clients.CLIENT_TWO,
  cl_model.Clients.CLIENT_THREE,
]

def send_many_requests():
  requests_amount = 100

  while requests_amount > 0:
    requests_amount -= 1
    request_sender.sendRequest(client_id = random.choice(cl_list))

    req_delay = random.expovariate(request_sender.lambda_req)
