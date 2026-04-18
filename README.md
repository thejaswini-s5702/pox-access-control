# POX Access Control Experiment
> SDN-based traffic filtering using the POX OpenFlow Controller and Mininet

---

## Problem Statement

In a Software Defined Network (SDN), the controller has full authority over
how traffic is forwarded across the network. This project implements
**access control** using the POX controller to:

- Allow communication **only** between host `h1` and host `h2`
- **Block** all other traffic (e.g., h3 cannot reach h1 or h2)
- Demonstrate OpenFlow flow rule installation on a virtual switch

---

## Network Topology

```
    h1 (10.0.0.1)
         \
          s1 ──── POX Controller (port 6633)
         /  \
h2 (10.0.0.2)  h3 (10.0.0.3)
```

- 1 Open vSwitch (`s1`)
- 3 hosts: `h1`, `h2`, `h3`
- Remote POX controller at `127.0.0.1:6633`

---

## Environment

| Component   | Version / Details                        |
|-------------|------------------------------------------|
| OS          | Linux 5.15.0-174-generic x86_64          |
| Python      | CPython 3.10.12 (Mar 3 2026)             |
| POX Version | 0.7.0 (gar)                              |
| Mininet     | Single topology, 3 hosts, 1 switch       |
| OpenFlow    | OpenFlow 1.0 (of_01)                     |

---

## Project Structure

```
pox-access-control/
│
├── access_control.py     ← Main SDN access control module (POX ext)
└── README.md             ← Project documentation
```

---

## Setup & Execution

### Prerequisites
- Ubuntu 20.04/22.04
- Python 3.6–3.9 (POX recommended) or 3.10 with warnings
- POX Controller
- Mininet

### Step 1 — Start the POX Controller

Open **Terminal 1**:
```bash
cd ~/pox
./pox.py log.level --DEBUG openflow.of_01 ext.access_control
```

**Actual output observed:**
```
POX 0.7.0 (gar) / Copyright 2011-2020 James McCauley, et al.
DEBUG:core:POX 0.7.0 (gar) going up...
DEBUG:core:Running on CPython (3.10.12/Mar 3 2026 11:56:32)
DEBUG:core:Platform is Linux-5.15.0-174-generic-x86_64-with-glibc2.35
INFO:core:POX 0.7.0 (gar) is up.
DEBUG:openflow.of_01:Listening on 0.0.0.0:6633
```

### Step 2 — Start Mininet

Open **Terminal 2**:
```bash
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6633
```

**Actual output observed:**
```
*** Creating network
*** Adding controller
*** Adding hosts: h1 h2 h3
*** Adding switches: s1
*** Adding links: (h1, s1) (h2, s1) (h3, s1)
*** Configuring hosts: h1 h2 h3
*** Starting controller: c0
*** Starting 1 switches: s1
*** Starting CLI:
mininet>
```

---

## Test Results

### Test 1 — h1 ping h2 (ALLOWED )

```bash
mininet> h1 ping h2
```

**Actual output:**
```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1  ttl=64 time=9.81 ms
64 bytes from 10.0.0.2: icmp_seq=2  ttl=64 time=0.181 ms
64 bytes from 10.0.0.2: icmp_seq=3  ttl=64 time=0.324 ms
...
64 bytes from 10.0.0.2: icmp_seq=16 ttl=64 time=0.164 ms

--- 10.0.0.2 ping statistics ---
16 packets transmitted, 16 received, 0% packet loss, time 15309ms
rtt min/avg/max/mdev = 0.132/0.853/9.813/2.325 ms
```
**Result: PASSED — h1 and h2 communicate successfully** 

---

### Test 2 — h2 ping h3 (BLOCKED )

```bash
mininet> h2 ping h3
```

**Actual output:**
```
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
From 10.0.0.2 icmp_seq=1  Destination Host Unreachable
From 10.0.0.2 icmp_seq=2  Destination Host Unreachable
...
From 10.0.0.2 icmp_seq=10 Destination Host Unreachable

--- 10.0.0.3 ping statistics ---
13 packets transmitted, 0 received, +10 errors, 100% packet loss, time 12115ms
```
**Result: PASSED — h2 to h3 traffic is blocked** 

---

### Test 3 — h1 ping h3 (BLOCKED )

```bash
mininet> h1 ping h3
```

**Actual output:**
```
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
From 10.0.0.1 icmp_seq=1  Destination Host Unreachable
From 10.0.0.1 icmp_seq=2  Destination Host Unreachable
...
From 10.0.0.1 icmp_seq=17 Destination Host Unreachable

--- 10.0.0.3 ping statistics ---
19 packets transmitted, 0 received, +17 errors, 100% packet loss, time 18328ms
```
**Result: PASSED — h1 to h3 traffic is blocked** 

---

## Flow Rules Installed on Switch s1

```bash
mininet> sh ovs-ofctl dump-flows s1
```

**Expected flow table:**
```
cookie=0x0, in_port="s1-eth1" actions=output:"s1-eth2"
cookie=0x0, in_port="s1-eth2" actions=output:"s1-eth1"
priority=0 actions=drop
```

| Rule | Match | Action |
|------|-------|--------|
| Rule 1 | Incoming from s1-eth1 (h1) | Forward to s1-eth2 (h2) |
| Rule 2 | Incoming from s1-eth2 (h2) | Forward to s1-eth1 (h1) |
| Rule 3 | Everything else (priority=0) | DROP |

---

## Summary of Results

| Test Case         | From → To   | Expected     | Actual Result         |
|-------------------|-------------|--------------|------------------------|
| Allowed traffic   | h1 → h2     | 0% loss      | 0% loss             |
| Blocked traffic   | h2 → h3     | 100% loss    | 100% loss            |
| Blocked traffic   | h1 → h3     | 100% loss    | 100% loss            |

---

## How the Controller Works

1. POX listens on port `6633` for switch connections
2. When switch `s1` connects, the controller installs flow rules:
   - Allow h1 ↔ h2 bidirectional traffic
   - Drop all other traffic with a low-priority default rule
3. The switch enforces these rules without consulting the controller again

---

## SDN Concepts Demonstrated

- OpenFlow controller-switch communication
- Flow rule installation (match + action)
- Default-deny access control policy
- Traffic isolation between hosts

---

## References

- [POX Controller GitHub](https://github.com/noxrepo/pox)
- [Mininet Documentation](http://mininet.org)
- Course materials and lab instructions provided by faculty

---

*Submitted by: Thejaswini  | SDN Lab Assignment*
SRN:PES2UG24CS563
