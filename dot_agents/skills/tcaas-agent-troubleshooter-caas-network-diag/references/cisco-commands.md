# Cisco NX-OS Troubleshooting Commands

## Port Diagnostics

```
show interface <port>                    # Full interface details (state, speed, errors, counters)
show interface <port> status             # One-line summary (status, vlan, duplex, speed, type)
show interface <port> counters           # Packet/byte counters (input/output, errors, discards)
show interface <port> counters errors    # Error counters only
show interface <port> switchport         # L2 config (access/trunk, allowed VLANs, native VLAN)
show interface <port> trunk              # Trunk details (allowed/active VLANs)
show interface <port> capabilities       # Port capabilities (speed, duplex, medium)
```

## MAC / ARP / Forwarding

```
show mac address-table interface <port>          # MAC addresses learned on port
show mac address-table vlan <vlan-id>            # All MACs in a VLAN
show ip arp interface <port>                     # ARP entries for port
show ip arp vlan <vlan-id>                       # ARP entries for VLAN
```

## VLAN Information

```
show vlan brief                          # All VLANs summary
show vlan id <vlan-id>                   # Specific VLAN details
show interface <port> switchport         # VLAN assignment for port
```

## Neighbor Discovery

```
show cdp neighbors                       # All CDP neighbors
show cdp neighbors interface <port>      # CDP neighbor on specific port
show lldp neighbors                      # All LLDP neighbors
show lldp neighbors interface <port>     # LLDP neighbor on specific port
```

## Spanning Tree

```
show spanning-tree interface <port>      # STP state for port
show spanning-tree vlan <vlan-id>        # STP topology for VLAN
```

## Logging & Events

```
show logging last 100                    # Recent log entries (100 lines)
show logging | include <port>            # Port-specific log history
show environment                         # Environmental alarms/warnings
show system uptime                       # System uptime
show interface <port> counters detailed  # Detailed counters with timestamps
```

## Port-Channel / Bond

```
show port-channel summary                # All port-channels
show port-channel database interface <po-id>  # Members of a port-channel
show lacp neighbor interface <port>      # LACP neighbor info
```

## Useful Patterns

- **Down port**: `show interface <port>` → check "line protocol is down" reason
- **Packet loss**: `show interface <port> counters errors` → check CRC, input/output errors
- **Wrong VLAN**: `show interface <port> switchport` → check access/trunk VLAN config
- **No MAC learned**: `show mac address-table interface <port>` → empty = no L2 connectivity
- **Flapping**: `show logging | include <port>` → check for up/down events
