# Lab Documentation

Network lab guides, runbooks, and setup documentation.

Arista and Cisco focused. Built on a physical lab environment running Arista 7050s, Arista 720s, Cisco Nexus, Palo Alto, and a Raspberry Pi 5 jump host.

---

## Contents

| Document | Description |
|---|---|
| [Pi5_Lab_JumpHost_Setup.md](Pi5_Lab_JumpHost_Setup.md) | Complete setup guide for deploying a Raspberry Pi 5 as a hardened, internet-accessible jump host bridging remote access to an isolated lab management network |

---

## Lab Architecture

```
MacBook/PC → Internet → Pi Jump Host (public IP)
                              ↓
                     Lab Management Network
                              ↓
              Arista 7050 (Spine) ←→ Arista 720 (Leaf)
              Cisco Nexus | Palo Alto | Opengear OOB
```

---

## Related Repositories

| Repo | Description |
|---|---|
| [nexus-config-tools](https://github.com/kloroxx/Nexus-config-tools) | Cisco Nexus configuration generators and templates |
| [network-automations](https://github.com/kloroxx/network-automations) | General Python scripts and network automation utilities |

---

## Author

Michael Nesteriak | [github.com/kloroxx](https://github.com/kloroxx) | [linkedin.com/in/lanlord](https://linkedin.com/in/lanlord)
