# mq
Try out message queue

## Eclipse Zenoh
The Eclipse Zenoh: Zero Overhead Pub/sub, Store/Query and Compute. [Website](zenoh.io)

Based on [zenoh-python examples](https://github.com/eclipse-zenoh/zenoh-python/tree/main/examples)

## Test Results
Ran a round trip latency test in a single process (`just pubsub`) and with two processes (`just fwd & just pub`).

- v1.7.0: mixed result.
  - Single host [MacOS]: Single and two-process test worked out-of-the-box. No additional configuration is needed (No `zenohd` router).
  - Single host [NixOS]: Single process test worked out-of-the-box, but two-process test failed to discover the other due to multicast not enabled by default for `lo` device.
  - Two hosts ([NixOS] -> [MacOS]): need `zenohd` router and start python script with `--connect tcp/{ZENOH_ROUTER_IP}:7447`.

### Host Configurations
Additional configuration on device is needed for `peer` mode.

1. Update firewall to allow multicast.

```bash
# Check iptable rules.
sudo iptables -L -v -n --line-numbers

# Allow multicast and put it at the top.
sudo iptables -I nixos-fw 1 -d 224.0.0.0/4 -j nixos-fw-accept

# Test multicast.
ping 224.0.0.1
```

2. (as needed) Turn on multicast on loopback device.

```bash
# Turn on multicast on loopback
sudo ip link set lo multicast on
```

### Test Stats
There are overhead associated with the 1st message. Look at the stats with and without the 1st message.

**Single process**
```
Stats:
Mean:	297.5 microseconds
sDev:	1084.1 microseconds
Min:	26.0 microseconds
Max:	5021.1 microseconds

Stats w/o 1st message:
Mean:	43.8 microseconds
sDev:	24.2 microseconds
Min:	26.0 microseconds
Max:	89.9 microseconds
```

**Two processes on ONE machine.**
```
Stats:
Mean:	603.5 microseconds
sDev:	1330.5 microseconds
Min:	144.0 microseconds
Max:	6390.1 microseconds

Stats w/o 1st message:
Mean:	293.5 microseconds
sDev:	90.0 microseconds
Min:	144.0 microseconds
Max:	425.1 microseconds
```

**Two processes on TWO machines.**
```
Stats:
Mean:	5645.3 microseconds
sDev:	1463.5 microseconds
Min:	4808.9 microseconds
Max:	9898.9 microseconds

Stats w/o 1st message:
Mean:	5205.6 microseconds
sDev:	393.2 microseconds
Min:	4808.9 microseconds
Max:	5861.0 microseconds
```
