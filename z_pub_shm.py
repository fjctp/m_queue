from datetime import datetime
import random
import string

from math import sqrt

from typing import List
from threading import Event
from common import Payload
import zenoh

def generate_rand_str(size: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

def print_stat(values: List[float], title: str):
    mean = lambda vals : sum(vals) / len(vals)
    def stddev(vals: List[float]) -> float:
        mu = mean(vals)
        return sqrt( sum( [(x - mu)**2 for x in vals] ) / len(vals))

    print("")
    print(title + ":")
    print(f"Mean:\t{mean(values):.1f} microseconds")
    print(f"sDev:\t{stddev(values):.1f} microseconds")
    print(f"Min:\t{min(values):.1f} microseconds")
    print(f"Max:\t{max(values):.1f} microseconds")

def main(conf: zenoh.Config, key_pub: str, key_sub: str, psize: int, iter: int, debug: bool):
    # initiate logging
    zenoh.init_log_from_env_or("error")

    print("Opening session...")
    with zenoh.open(conf) as session:
        e = Event()
        time_elapse = []

        print(f"Declaring Subscriber on '{key_sub}'...")
        def listener(sample: zenoh.Sample):
            p = Payload.loads(sample.payload.to_bytes())

            ms = (datetime.now().timestamp() - p.timestamp) *1e6
            time_elapse.append(ms)

            e.set() # Unpause publisher
        session.declare_subscriber(key_sub, listener)

        print("Creating POSIX SHM provider...") if debug else None
        provider = zenoh.shm.ShmProvider.default_backend(1024 * 1024)

        print(f"Declaring Publisher on '{key_pub}'...")
        pub = session.declare_publisher(key_pub)

        print("Press CTRL-C to quit...")
        for message in [generate_rand_str(psize) for idx in range(iter)]:
            pobj = Payload(datetime.now().timestamp(), message)
            ss = pobj.encode()

            sbuf = provider.alloc(
                len(ss),
                policy=zenoh.shm.BlockOn(zenoh.shm.GarbageCollect()),
            )
            sbuf[:] = ss.encode()

            print(f"Putting Data ('{key_pub}': '{sbuf}')...") if debug else None
            pub.put(sbuf)

            # Wait for sbscriber to receive the message.
            e.clear()
            e.wait()
    
    assert(len(time_elapse) == iter)
    print_stat(time_elapse, "Stats")
    print_stat(time_elapse[2:], "Stats w/o 1st message") # discard the 1st message due to overhead.
    
    print([round(x, 2) for x in time_elapse]) if debug else None

if __name__ == "__main__":
    import argparse

    import common

    parser = argparse.ArgumentParser(
        prog="z_pub_shm", description="zenoh pub example"
    )
    common.add_config_arguments(parser)
    parser.add_argument(
        "--pub",
        "-1",
        dest="pub",
        default="demo/example/ping",
        type=str,
        help="The key expression to publish onto.",
    )
    parser.add_argument(
        "--sub",
        "-2",
        dest="sub",
        default="demo/example/pong",
        type=str,
        help="The key expression to subscribe to.",
    )
    parser.add_argument(
        "--iter",
        "-i",
        dest="iter", 
        default=10,
        type=int, 
        help="How many puts to perform."
    )
    parser.add_argument(
        "--psize",
        "-s",
        dest="psize",
        default=10,
        type=int, 
        help="Payload size in byte."
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug output."
    )

    args = parser.parse_args()
    conf = common.get_config_from_args(args)

    main(conf, args.pub, args.sub, args.psize, args.iter, args.debug)
