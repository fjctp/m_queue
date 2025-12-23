fwd OPT="":
  # Start message forwarder
  python3 z_fwd_shm.py {{OPT}}

pub OPT="":
  # Start message publisher
  python3 z_pub_shm.py -i 20 -s 1024 {{OPT}}

pubsub OPT="":
  # Start message publisher and subscriber in a single process
  python3 z_pub_shm.py -1 'demo/example/ping' -2 'demo/example/ping' -i 20 -s 1024 {{OPT}}

init:
  # Initialize the directory.
  python3 -m venv .venv
  source .venv/bin/activate.fish
  pip install eclipse-zenoh --no-binary :all: --config-settings build-args="--features=zenoh/shared-memory"
  