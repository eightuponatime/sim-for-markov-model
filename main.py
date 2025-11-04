import RequestSender
from models import Clients as cl_model
from models import ResponseModel
import random
import simpy

LAMBDA_RATE = 15
SIMULATION_DURATION = 20
CALIBRATION_REQUESTS = 10

cl_list = [
  cl_model.Clients.CLIENT_ONE,
  cl_model.Clients.CLIENT_TWO,
  cl_model.Clients.CLIENT_THREE,
]

def send_exp_time_requests(env, request_sender, duration):
  requests_count = 0
  
  while env.now < duration:
    interarrival_time = random.expovariate(LAMBDA_RATE)
    yield env.timeout(interarrival_time)
    
    requests_count += 1
    client_id = random.choice(cl_list)
    print(f"\n[{env.now:.2f}s] generating request #{requests_count} for {client_id.value}")
    
    env.process(request_sender.send_request_process(client_id))

if __name__ == "__main__":
  env = simpy.Environment()
  request_sender = RequestSender.RequestSender(env, LAMBDA_RATE)

  print("calibration check")
  calibration_stats = request_sender.calibrate_avg_time(
    num_requests=CALIBRATION_REQUESTS
  )
  
  if calibration_stats is None:
    print("calibration error")
    exit(1)
  
  print("simulation")
  print(f"duration: {SIMULATION_DURATION}s")
  print(f"lambda rate: {LAMBDA_RATE} requests/sec")
  print(f"expected requests: ~{LAMBDA_RATE * SIMULATION_DURATION}")
  
  env.process(send_exp_time_requests(env, request_sender, SIMULATION_DURATION))
  
  env.run(until=SIMULATION_DURATION)
  
  print("\n")
  request_sender.print_simulation_results()