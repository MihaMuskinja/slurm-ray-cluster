import ray
import os


@ray.remote
def get_id():
    return os.getpid()


if __name__ == "__main__":
    ray.init(num_cpus=8)

    ids = []
    for _ in range(1000):
        ids += [get_id.remote()]

    ids = set(ray.get(ids))
    print(ids)
