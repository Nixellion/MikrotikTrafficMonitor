# Mikrotik Traffi cMonitor

Mikrotik Traffic Monitor is a relatively small and lightweight server-side
tool to collect and process Accounting data from Mikrotik routers running RouterOS and
present them in a form that's easy to analyze.

It uses python Flask for the server side of things.

# Installation

```bash
cd /opt/
git clone GIT_URL
apt install python3 python3-pip python3-dev
cd MikrotikTrafficMonitor
pip3 install -r requirements.txt
cp MikrotikTrafficMonitor.service /lib/systemd/system
systemctl enable MikrotikTrafficMonitor
service MikrotikTrafficMonitor start
systemctl status MikrotikTrafficMonitor
```

# Setting up Router

You need to go into IP - Accounting and enable Accounting, also enable Web Access and
type the IP of the machine where this tool will run on.

You may also need to disable fast track as it ignores accounting.