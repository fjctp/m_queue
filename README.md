# mq
Try out message queue

## Eclipse Zenoh
The Eclipse Zenoh: Zero Overhead Pub/sub, Store/Query and Compute. [Website](zenoh.io)

Based on [zenoh-python examples](https://github.com/eclipse-zenoh/zenoh-python/tree/main/examples)

## Test Results
Ran a round trip latency test in a single process (`just pubsub`) and with two processes (`just fwd & just pub`).

- v1.7.0: mixed result.
  - Single and two-process test worked out-of-the-box on [MacOS]. No additional configuration is needed (No `zenohd` router).
  - Single process test worked out-of-the-box on [NixOS], but two-process test failed to discover the other due to multicast not enabled by default for `lo` device.

```bash
# Turn on mutlicast on loopback
sudo ip link set lo multicast on

# Add route for mutlicast
sudo ip route add 224.0.0.0/4 dev lo
```
### Test Stats
There are overhead associated with the 1st message. Look at the stats with and without the 1st message.

**Test result from single process test.**
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

**Test result from two-process test.**
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