
sub:
  python3 z_sub_shm.py

pub:
  python3 z_pub_shm.py -i 20 -s 1024

pubsub:
  python3 z_pub_shm.py -1 'demo/example/ping' -2 'demo/example/ping' -i 20 -s 1024

init:
  python3 -m venv .venv
  source .venv/bin/activate.fish
  pip install eclipse-zenoh --no-binary :all: --config-settings build-args="--features=zenoh/shared-memory"
  