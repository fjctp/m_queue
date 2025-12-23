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

def print_stat(values: List[float]):
    nn = len(values)
    mean = sum(values) / nn
    stddev = sqrt( sum( [(x - mean)**2 for x in values] ) / nn)

    print("")
    print(f"Mean:\t{mean:.1f} microseconds")
    print(f"sDev:\t{stddev:.1f} microseconds")
    print(f"Min:\t{min(values):.1f} microseconds")
    print(f"Max:\t{max(values):.1f} microseconds")

def main(conf: zenoh.Config, key: str, psize: int, iter: int, debug: bool):
    # initiate logging
    zenoh.init_log_from_env_or("error")

    print("Opening session...")
    with zenoh.open(conf) as session:
        key_pub = f"{key}/ping"
        key_sub = key_pub
        # key_sub = f"{key}/pong"
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
    print_stat(time_elapse)

if __name__ == "__main__":
    import argparse

    import common

    parser = argparse.ArgumentParser(
        prog="z_pub_shm", description="zenoh pub example"
    )
    common.add_config_arguments(parser)
    parser.add_argument(
        "--key",
        "-k",
        dest="key",
        default="demo/example",
        type=str,
        help="The key expression to publish onto.",
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

    main(conf, args.key, args.psize, args.iter, args.debug)
