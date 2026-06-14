# Juniper JunOS Troubleshooting Commands

## Port Diagnostics

```
show interfaces <port>                   # Interface summary (status, speed, traffic)
show interfaces <port> extensive         # Full details (errors, counters, optics, flaps)
show interfaces <port> detail            # Detailed view (less verbose than extensive)
show interfaces <port> statistics        # Traffic statistics
show interfaces terse                    # All interfaces one-line summary
```

## MAC / ARP / Forwarding

```
show ethernet-switching table interface <port>          # MAC addresses on port
show ethernet-switching table vlan-name <vlan>          # All MACs in a VLAN
show arp interface <port>                               # ARP entries for port
show ethernet-switching mac-ip-table interface <port>   # MAC-IP bindings
```

## VLAN Information

```
show vlans                               # All VLANs summary
show vlans <vlan-name>                   # Specific VLAN details
show vlans interface <port>              # VLANs on specific port
show configuration interfaces <port>     # Interface VLAN config
```

## Neighbor Discovery

```
show lldp neighbors                      # All LLDP neighbors
show lldp neighbors interface <port>     # LLDP neighbor on specific port
show lldp detail                         # Detailed LLDP info
```

## Spanning Tree

```
show spanning-tree interface <port>      # STP state for port
show spanning-tree bridge                # STP bridge info
```

## Logging & Events

```
show log messages | last 100             # Recent log entries (100 lines)
show log messages | match <port> | last 50   # Port-specific log history (link up/down events)
show system alarms                       # Active system alarms
show chassis alarms                      # Active chassis/hardware alarms
show system uptime                       # System uptime, last boot, last config change
show interfaces <port> extensive | match "error|drop|flap"  # Error summary
```

### Log Analysis Tips

- **ARP DDoS alarms** (`DDOS_PROTOCOL_VIOLATION_SET/CLEAR` for Overlay:arp) occurring daily around midnight are typically normal/known behavior — they self-clear in 3-8 minutes.
- **Link flap events** show as `SNMP_TRAP_LINK_DOWN` / `SNMP_TRAP_LINK_UP` pairs. Frequent flapping (multiple per hour) indicates cable, optic, or NIC issues.
- **SSH rate limiting** (`ssh exceeded counts/min limit 5/min`) — avoid rapid successive SSH connections to the same switch.
- **FPC Management Ethernet Link Down** — common alarm on lab/dev switches, typically non-critical if data plane is unaffected.

## LAG / Aggregated Ethernet

```
show lacp interfaces                     # All LACP interfaces
show lacp interfaces <ae-port>           # Specific LAG members
show interfaces <ae-port>               # Aggregated interface status
```

## Useful Patterns

- **Down port**: `show interfaces <port>` → check "Physical link is Down"
- **Packet loss**: `show interfaces <port> extensive` → check Input/Output errors
- **Wrong VLAN**: `show vlans interface <port>` → check VLAN membership
- **No MAC**: `show ethernet-switching table interface <port>` → empty = no L2 connectivity
- **Flapping**: `show interfaces <port> extensive | match flap` → check Last flapped timestamp
- **Optics**: `show interfaces diagnostics optics <port>` → check SFP power levels
