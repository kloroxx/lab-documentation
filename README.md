# Nexus 9K VPC Pair Config Generator

Generates Cisco NX-OS configuration for a pair of **Nexus 93240YC-FX2** switches deployed as a VPC pair, replacing an existing Nexus 5K pair.

---

## Use Case

Hardware refresh — Nexus 5548/5596 → Nexus 93240YC-FX2. Maintains existing VPC architecture without migrating to spine/leaf. Supports up to 10 FEX units carried forward from the 5K environment.

---

## Architecture

```
[Nexus 7K Core]
      |
   [7K uplinks - L2 VPC, all VLANs]
      |
[9K-SW1] === peer-link === [9K-SW2]   <-- VPC pair (replaces 5K pair)
      |                         |
   [FEX 101..110]           [FEX 101..110]  <-- dual-homed FEX
```

---

## How It Works

Three pieces work together to generate your switch configs:

### 1 — `variables_template.yml` (Your Input Form)
This is where you fill in the real values for your environment — hostnames, IP addresses, VLANs, NTP servers, TACACS keys, SNMP communities, and so on. Think of it like a questionnaire about the specific site you are deploying.

### 2 — `nexus9k_vpc_template.j2` (The Config Skeleton)
This is the configuration template. It contains the full structure of a proper Nexus 9K VPC config with placeholders where site-specific values go — similar to a mail merge document. It never changes between sites. You never need to edit this file.

### 3 — `generate.py` (The Engine)
This is the Python script that ties everything together. It reads your variables file, feeds those values into the template, and produces finished NX-OS config files — one per switch — ready to apply.

### What Jinja2 Is Doing
When the template sees this:
```
hostname {{ sw.hostname }}
```
And your variables file says:
```yaml
switch1:
  hostname: "NYC-9K-01"
```
The script replaces `{{ sw.hostname }}` with `NYC-9K-01` in the output. Every `{{ }}` in the template is a variable substitution. Every `{% for %}` loop automatically generates repeated config blocks — for example, one FEX stanza per FEX unit — without you having to write each one manually.

---

## Features Generated

- VPC domain with peer keepalive over mgmt0
- Port-channel peer-link
- L2 uplinks to Nexus 7K core (all VLANs)
- HSRP active/standby on all SVIs (Switch 1 active, Switch 2 standby)
- FEX associations (variable count up to 10)
- Jumbo frames (MTU 9216)
- OOB management on mgmt0
- NTP, SNMP, TACACS+, Syslog

---

## Requirements

```bash
pip install jinja2 pyyaml netaddr
```

---

## Step-by-Step Usage

### Step 1 — Copy the template and fill in your values
```bash
cp variables_template.yml variables.yml
nano variables.yml
```

Replace every `x.x.x.x` and placeholder value with real values for your site. This file stays local — it is gitignored and will never be pushed to GitHub.

### Step 2 — Run the generator
```bash
# Interactive mode — prompts you to choose which switch
python3 generate.py

# Generate both switch configs at once
python3 generate.py --both

# Generate a specific switch only
python3 generate.py --switch 1
python3 generate.py --switch 2

# Use a custom variables file
python3 generate.py --vars my_site_vars.yml
```

### Step 3 — Find your generated configs
```bash
ls generated_configs/
```

Output files are named with the switch hostname and a timestamp:
```
generated_configs/
  NYC-9K-01_SW1_20260428_110000.cfg
  NYC-9K-02_SW2_20260428_110000.cfg
```

Review the configs before applying to production equipment.

---

## File Structure

```
.
├── generate.py                 # Main script — runs the generator
├── nexus9k_vpc_template.j2     # Jinja2 config template — never edit directly
├── variables_template.yml      # Sanitized template — safe for GitHub
├── variables.yml               # Your real values — DO NOT commit to GitHub
├── .gitignore                  # Excludes variables.yml and generated configs
└── generated_configs/          # Output directory — gitignored
```

---

## Customization

- **Add VLANs** — edit the `vlans` list in `variables.yml`
- **Add SVIs** — edit the `svis` list — each SVI gets HSRP automatically
- **Add FEX units** — add entries to `fex_units` list (tested up to 10)
- **Change uplink interfaces** — edit `uplink.switch1_interfaces` and `switch2_interfaces`
- **Change peer-link interfaces** — edit `peer_link.interfaces`

---

## Security

`variables.yml` contains credentials and IP addresses specific to your environment. It is excluded from Git via `.gitignore`. Only `variables_template.yml` with placeholder values is committed to GitHub.

**Never commit real credentials, SNMP communities, TACACS keys, or internal IP addresses to a public repository.**

---

## Author

Michael Nesteriak | [github.com/kloroxx](https://github.com/kloroxx)
