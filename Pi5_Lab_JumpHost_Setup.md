# Raspberry Pi 5 — Lab Jump Host Setup Guide
**Author:** Michael Nesteriak | Lab Infrastructure  
**Last Updated:** April 2026

---

## Overview

This document captures the complete setup process to deploy a Raspberry Pi 5 as a secure, always-on jump host bridging remote internet access to an isolated lab management network.

**Architecture:**
```
MacBook/PC → Internet → Pi (eth1 public IP) → Lab Management Network (eth0) → Lab Gear
```

---

## Hardware

- CanaKit Raspberry Pi 5 Desktop PC — Fully Assembled (8GB RAM, 256GB NVMe)
- USB 3.0 Gigabit Ethernet Adapter (second NIC)
- Two network connections:
  - **eth0** — Built-in NIC → Lab management L2 network
  - **eth1** — USB NIC → Cable modem (internet/public IP)

---

## Phase 1 — Initial Boot and System Update

1. Boot Pi — complete first-run setup wizard, set strong password
2. Open terminal and run full system update:
```bash
sudo apt update && sudo apt full-upgrade -y
```
3. Reboot after updates complete:
```bash
sudo reboot
```

---

## Phase 2 — Enable SSH

Raspberry Pi OS uses socket-based SSH activation. Enable and configure it:

```bash
# Enable via raspi-config
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable

# Disable socket activation (required for custom port)
sudo systemctl disable --now ssh.socket

# Set SSH port to 2222
echo "Port 2222" | sudo tee -a /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart ssh

# Verify listening on correct port
sudo systemctl status ssh
```

---

## Phase 3 — Generating SSH Key Pairs (Client Side)

Each user generates their own SSH key pair on their own machine and sends their **public key** to the Pi administrator. Never share the private key.

### Mac

Open Terminal: `Command + Space` → type Terminal → Enter

```bash
ssh-keygen -t ed25519 -C "your-name-lab"
```

Accept the default path. Set a passphrase when prompted.

Print your public key to copy and send:
```bash
cat ~/.ssh/id_ed25519.pub
```

Output looks like:
```
ssh-ed25519 AAAAC3Nza....long string....your-name-lab
```

Copy the entire line and send to the Pi administrator.

---

### Windows

Open PowerShell: `Windows Key` → type PowerShell → Enter

```powershell
ssh-keygen -t ed25519 -C "your-name-lab"
```

Accept the default path (`C:\Users\<yourname>\.ssh\id_ed25519`). Set a passphrase when prompted.

Print your public key to copy and send:
```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

Output looks like:
```
ssh-ed25519 AAAAC3Nza....long string....your-name-lab
```

Copy the entire line and send to the Pi administrator.

---

### Key Rules
- **Public key** (`id_ed25519.pub`) — safe to share, send to administrator
- **Private key** (`id_ed25519`) — never share with anyone under any circumstances
- Administrator only ever needs the `.pub` file

---

## Phase 4 — SSH Key Authentication on Pi

Copy public key to the Pi from client Mac:
```bash
ssh-copy-id -p 22 remote-admin@<pi-local-ip>
```

On the **Pi**, disable password authentication:
```bash
sudo nano /etc/ssh/sshd_config
```
Set:
```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```
Restart SSH:
```bash
sudo systemctl restart ssh
```

---

## Phase 5 — Firewall (UFW)

```bash
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp
sudo ufw enable
sudo ufw status
```

Expected output — only 2222/tcp allowed inbound.

---

## Phase 6 — Fail2ban

```bash
sudo apt install fail2ban -y
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo systemctl status fail2ban
```

---

## Phase 7 — Disable Unnecessary Services

```bash
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

---

## Phase 8 — Network Configuration (Static Public IP)

Pi uses NetworkManager. Configure eth1 with static public IP:

```bash
# View connections
sudo nmcli con show

# Configure static IP on eth1 (Wired connection 2)
sudo nmcli con mod "Wired connection 2" ipv4.method manual ipv4.addresses "<PUBLIC_IP>/<PREFIX>" gw4 "<GATEWAY>" ipv4.dns "8.8.8.8 8.8.4.4"

# Disable IPv6 on eth1
sudo nmcli con mod "Wired connection 2" ipv6.method disabled

# Set route metric to prefer eth1 as default (lower = preferred)
sudo nmcli con mod "Wired connection 2" ipv4.route-metric 50

# Apply changes
sudo nmcli con down "Wired connection 2"
sudo nmcli con up "Wired connection 2"
```

Verify:
```bash
ip addr show eth1
ip route show default
curl -4 ifconfig.me
```

---

## Phase 9 — Default Route Fix

If default route disappears after interface restart, add persistent route:

```bash
sudo nmcli con mod "Wired connection 2" ipv4.routes "0.0.0.0/0 <GATEWAY> 50"
sudo nmcli con down "Wired connection 2"
sudo nmcli con up "Wired connection 2"
```

Verify eth1 shows as default route at metric 50, eth0 at metric 101.

---

## Phase 10 — ISP/Modem Configuration

**Required:** Cable modem must be in **bridge mode** for public IPs to route directly to Pi.

- Contact ISP (Spectrum Business: 1-800-314-7195)
- Request modem be placed in bridge mode
- Modem becomes transparent — public /28 block routes directly to Pi
- No NAT, no port forwarding required

---

## Phase 11 — Adding Additional Users

```bash
# Create user
sudo adduser <username>
sudo usermod -aG sudo <username>

# Create SSH directory and authorized_keys file
sudo mkdir /home/<username>/.ssh
sudo touch /home/<username>/.ssh/authorized_keys
sudo nano /home/<username>/.ssh/authorized_keys
# Paste their public key, save with Ctrl+X, Y, Enter

# Set correct permissions
sudo chown -R <username>:<username> /home/<username>/.ssh
sudo chmod 700 /home/<username>/.ssh
sudo chmod 600 /home/<username>/.ssh/authorized_keys
```

User connects with:

**Mac:**
```bash
ssh -p 2222 <username>@<PUBLIC_IP>
```

**Windows (PowerShell):**
```powershell
ssh -p 2222 <username>@<PUBLIC_IP>
```

---

## Phase 12 — Reboot Validation

After all configuration is complete, reboot and confirm everything survives:

```bash
sudo reboot
```

After 60 seconds, test from client machine:

**Mac:**
```bash
ssh -p 2222 remote-admin@<PUBLIC_IP>
```

**Windows:**
```powershell
ssh -p 2222 remote-admin@<PUBLIC_IP>
```

---

## Final State

| Item | Value |
|------|-------|
| eth0 | Lab management network (DHCP) |
| eth1 | Public IP /28 (static) |
| SSH Port | 2222 |
| Authentication | Key only — no passwords |
| Firewall | UFW — deny all except 2222/tcp |
| Fail2ban | Running |
| Default route | eth1 at metric 50 |
| Bluetooth | Disabled |
| Avahi | Disabled |

---

*Replace `<PUBLIC_IP>`, `<PREFIX>`, and `<GATEWAY>` with your actual network values throughout this document.*
