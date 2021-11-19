#!/usr/bin/env python
"""
A simple test of Ray

This example uses placement_group API to spread work around

"""

from pprint import pprint
import os
import platform
import ray
import time


def build_nodes_resource_list(redis_ip: str):
    nodes = ray.nodes()
    resource_list = list()
    for node in nodes:
        naddr = node['NodeManagerAddress']
        if naddr == redis_ip:
            continue
        else:
            resource_list.append(node)
    return resource_list


@ray.remote
class actor():
    def __init__(self) -> None:
        self.pid = os.getpid()
        self.hostname = platform.node()
        self.ip = ray._private.services.get_node_ip_address()
        print(f"Initial message from PID - {self.pid} Running on host - {self.hostname} {self.ip}")

    def ping(self):
        print(f"{self.pid} {self.hostname} {self.ip} - ping")
        time.sleep(5)
        return f"{self.pid} {self.hostname} {self.ip} - pong"


def main(redis_ip):

    # show the ray cluster
    print(f"Ray Cluster resources : {ray.cluster_resources()}")

    # Get list of nodes to use
    nodes = build_nodes_resource_list(redis_ip)
    print(f"Found {len(nodes)} Worker nodes in the Ray Cluster:")
    pprint(nodes)
    print(" ")

    # Setup one Actor per node
    print(f"Setting up {len(nodes)} Actors...")
    actors = []
    for node in nodes:
        node_ip_str = f"node:{node['NodeManagerAddress']}"
        actors.append(actor.options(resources={f"{node_ip_str}": 1}).remote())
    time.sleep(1)

    # Ping-Pong test
    for _ in range(5):
        messages = [actor.ping.remote() for actor in actors]
        for msg in ray.get(messages):
            print(f"Received back message {msg}")

    # now terminate the actors
    [ray.kill(actor) for actor in actors]


if __name__ == "__main__":
    # ip_head and redis_passwords are set by ray cluster shell scripts
    print(os.environ["ip_head"], os.environ["redis_password"])
    ray.init(address='auto', _node_ip_address=os.environ["ip_head"].split(":")[0], _redis_password=os.environ["redis_password"])

    # run main
    main(redis_ip=os.environ["ip_head"].split(":")[0])
