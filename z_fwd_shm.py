"""
z_fwd_shm — Forwarder using POSIX shared memory (SHM) provider.

Usage:
    python z_fwd_shm.py [--pub KEY] [--sub KEY] [--debug]

This small utility subscribes to a `key_sub` key and republishes
received samples onto `key_pub` key.
"""

import zenoh
from common import Payload

def main(conf: zenoh.Config, key_pub: str, key_sub: str, debug: bool):
    # initiate logging
    zenoh.init_log_from_env_or("error")

    print("Opening session...")
    with zenoh.open(conf) as session:
        print(f"Declaring Publisher on '{key_pub}'...")
        pub = session.declare_publisher(key_pub)
        
        print(f"Declaring Subscriber on '{key_sub}'...")
        with session.declare_subscriber(key_sub) as sub:
            print("Press CTRL-C to quit...")
            for sample in sub:
                _, payload = handle_bytes(sample.payload)
                pub.put(sample.payload)

                if debug:
                    pobj = Payload.loads(payload)
                    print(pobj)


def handle_bytes(bytes: zenoh.ZBytes) -> tuple[str, str]:
    bytes_type = "SHM" if bytes.as_shm() is not None else "RAW"
    return bytes_type, bytes.to_string()

if __name__ == "__main__":
    import argparse
    import common

    parser = argparse.ArgumentParser(
        prog="z_fwd_shm", description="Forward received package from 'sub' to 'pub' key."
    )
    common.add_config_arguments(parser)
    parser.add_argument(
        "--pub",
        "-1",
        dest="pub",
        default="demo/example/pong",
        type=str,
        help="The key expression to publish onto.",
    )
    parser.add_argument(
        "--sub",
        "-2",
        dest="sub",
        default="demo/example/ping",
        type=str,
        help="The key expression to subscribe to.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug output."
    )

    args = parser.parse_args()
    conf = common.get_config_from_args(args)

    main(conf, args.pub, args.sub, args.debug)
