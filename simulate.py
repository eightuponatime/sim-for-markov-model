import simpy

env = simpy.Environment()
nsp_requests = simpy.Resource(env, capacity=2)
