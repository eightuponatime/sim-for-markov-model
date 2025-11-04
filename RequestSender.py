import requests
import models.Clients as cl
from models import ResponseModel as rm
from models import CalibrateStatsModel as csm
import json
import simpy
import random
from typing import List
import statistics

class RequestSender:
  baseUrl = "http://localhost:8080"

  def __init__(self,
               env: simpy.Environment,
               lambda_rate: float = 10):
    self.env = env
    self.lambda_rate = lambda_rate
    self.calibrated_avg_time = None
    self.successful_requests = 0
    self.blocked_requests = 0

  def get_server_metrics(self):
    response = requests.get(f"{self.baseUrl}/metrics")

    if response.status_code == 200:
      return response.json()
    else:
      return None

  def send_request_to_server(self, client_id: str) -> rm.ResponseModel | None:
    body = { "client_id": client_id }
    json_payload = json.dumps(body)
    url = f"{self.baseUrl}/process"

    try:
      r = requests.post(url, data=json_payload, headers={"Content-Type": "application/json"})

      print(f"[{self.env.now:.2f}s] Client {client_id}: status code -> {r.status_code}")

      if r.status_code == 200:
        data = r.json()
        response_model = rm.ResponseModel(
          buffer_size = data["buffer_size"],
          client_id = data["client_id"],
          status = True, 
          phase1_time_ms = data["phase1_time_ms"],
          phase2_time_ms = data["phase2_time_ms"],
          phase3_time_ms = data["phase3_time_ms"],
          total_time_ms = data["total_time_ms"],
        )

        self.successful_requests += 1
        return response_model
      else:
        print(f"[{self.env.now:.2f}s] request blocked: {r.json()}")
        self.blocked_requests += 1
        return None
    except Exception as e:
      print(f"[{self.env.now:.2f}s] error while sending response: {e}")
      self.blocked_requests += 1
      return None

  # simpy process
  def send_request_process(self, client):
    client_id = client.value
    # response = self.send_request_to_server(client_id)  
    service_time = random.expovariate(1.0 / self.calibrated_avg_time)

    yield self.env.timeout(service_time)

    mu_system = 1.0 / self.calibrated_avg_time
    rho = self.lambda_rate / mu_system

    if rho < 1.0:
      block_prob = 0.0
    elif rho < 2.0:
      block_prob = 0.2
    elif rho < 5.0:
      block_prob = 0.5
    else:
      block_prob = 0.8
    
    if random.random() < block_prob:
      self.blocked_requests += 1
    else: self.successful_requests += 1

    # if response:
    #   yield self.env.timeout(response.total_time_ms / 1000)
    # else:
    #   yield self.env.timeout(0.001)

  def calibrate_avg_time(self, num_requests: int = 10) -> csm.CallibrateStatsModel | None:
    print(f"calibration with {num_requests} requests")

    clients_list = [
      cl.Clients.CLIENT_ONE.value,
      cl.Clients.CLIENT_TWO.value,
      cl.Clients.CLIENT_THREE.value
    ]

    total_times = []
    phase1_times = []
    phase2_times = []
    phase3_times = []
    successful = 0
    blocked = 0

    for i in range(num_requests):
      rand_client_id = random.choice(clients_list)
      print(f"calibration request {i+1}/{num_requests}: client -> {rand_client_id}")

      body = {"client_id": rand_client_id}
      json_payload = json.dumps(body)
      url = f"{self.baseUrl}/process"

      try:
        r = requests.post(url, data=json_payload, headers={"Content-Type": "application/json"})

        if r.status_code == 200:
          data = r.json()
          total_times.append(data["total_time_ms"])
          phase1_times.append(data["phase1_time_ms"])
          phase2_times.append(data["phase2_time_ms"])
          phase3_times.append(data["phase3_time_ms"])
          successful += 1
          print(f"success: total={data['total_time_ms']:.2f}ms, buffer={data['buffer_size']}")
        else:
          blocked += 1
          print(f"blocked: {r.json().get('error', 'unknown error')}")
      except Exception as e:
        blocked += 1
        print(f"error: {e}")

    if len(total_times) > 0:
      stats = csm.CallibrateStatsModel(
        avg_total_time_ms = statistics.mean(total_times),
        avg_phase1_time_ms = statistics.mean(phase1_times),
        avg_phase2_time_ms = statistics.mean(phase2_times),
        avg_phase3_time_ms = statistics.mean(phase3_times),
        successful_requests = successful,
        blocked_requests = blocked,
        blocking_probability = blocked / num_requests
      )

      self.calibrated_avg_time = stats.avg_total_time_ms / 1000

      print("calibration results:")
      print(f"avg total time: {stats.avg_total_time_ms:.2f} ms")
      print(f"\tPhase 1: {stats.avg_phase1_time_ms:.2f} ms")
      print(f"\tPhase 2: {stats.avg_phase2_time_ms:.2f} ms")
      print(f"\tPhase 3: {stats.avg_phase3_time_ms:.2f} ms")
      print(f"successful: {stats.successful_requests}/{num_requests}")
      print(f"blocked: {stats.blocked_requests}/{num_requests}")
      print(f"blocking probability: {stats.blocking_probability:.2%}")
      print(f"{'='*60}\n")

      return stats
    else:
      print("\nno successful requests during calibration")
      return None

  def print_simulation_results(self):
    total = self.successful_requests + self.blocked_requests
    if total > 0:
      print(f"\n{'='*60}")
      print("Simulation Results:")
      print(f"{'='*60}")
      print(f"Total requests: {total}")
      print(f"Successful: {self.successful_requests}")
      print(f"Blocked: {self.blocked_requests}")
      print(f"Blocking probability: {self.blocked_requests/total:.2%}")
      print(f"{'='*60}\n")

      metrics = self.get_server_metrics()
      if metrics:
        print("Server-side metrics:")
        print(f"  Total requests: {metrics['total_requests']}")
        print(f"  Blocked requests: {metrics['blocked_requests']}")
        print(f"  Blocking probability: {metrics['blocking_probability']:.2%}")
        print(f"  Avg phase 1 time: {metrics['avg_phase1_time']:.4f}s")
        print(f"  Avg phase 2 time: {metrics['avg_phase2_time']:.4f}s")
        print(f"  Avg phase 3 time: {metrics['avg_phase3_time']:.4f}s")
        print(f"  Avg total time: {metrics['avg_total_time']:.4f}s")
        print(f"  Avg buffer size: {metrics['avg_buffer_size']:.2f}")