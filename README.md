# Nexus 9K VPC Pair Config Generator

Generates Cisco NX-OS configuration for a pair of **Nexus 93240YC-FX2** switches deployed as a VPC pair, replacing an existing Nexus 5K pair.

## Use Case

Hardware refresh — Nexus 5548/5596 → Nexus 93240YC-FX2. Maintains existing VPC architecture without migrating to spine/leaf. Supports up to 10 FEX units carried forward from the 5K environment.

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

## Features Generated

- VPC domain with peer keepalive over mgmt0
- Port-channel peer-link
- L2 uplinks to Nexus 7K core (all VLANs)
- HSRP active/standby on all SVIs
- FEX associations (variable count up to 10)
- Jumbo frames (MTU 9216)
- NTP, SNMP, TACACS+, Syslog
- OOB management on mgmt0

## Requirements

```bash
pip install jinja2 pyyaml netaddr
```

## Usage

```bash
# Copy template and fill in your values
cp variables_template.yml variables.yml
# Edit variables.yml with your environment details

# Interactive mode
python3 generate.py

# Generate both switch configs at once
python3 generate.py --both

# Generate specific switch
python3 generate.py --switch 1
python3 generate.py --switch 2

# Use a custom variables file
python3 generate.py --vars my_site_vars.yml
```

## Output

Configs are saved to `./generated_configs/` with hostname and timestamp:
```
generated_configs/
  NYC-9K-01_SW1_20260420_143022.cfg
  NYC-9K-02_SW2_20260420_143022.cfg
```

## File Structure

```
.
├── generate.py                 # Main script
├── nexus9k_vpc_template.j2     # Jinja2 config template
├── variables_template.yml      # Sanitized template — safe for GitHub
├── variables.yml               # Your values — DO NOT commit to GitHub
├── .gitignore                  # Excludes variables.yml and generated configs
└── generated_configs/          # Output directory — gitignored
```

## Security

`variables.yml` contains credentials and IP addresses. It is excluded from Git via `.gitignore`. Only `variables_template.yml` with placeholder values is committed to GitHub.

Never commit real credentials, SNMP communities, TACACS keys, or internal IP addresses to a public repository.

## Customization

- **Add VLANs:** Edit the `vlans` list in `variables.yml`
- **Add SVIs:** Edit the `svis` list — each SVI gets HSRP automatically
- **Add FEX:** Add entries to `fex_units` list (tested up to 10)
- **Change uplink interfaces:** Edit `uplink.switch1_interfaces` and `switch2_interfaces`

## Author

Michael Nesteriak | [github.com/kloroxx](https://github.com/kloroxx)
