# Mikrotik Traffic Monitor

Mikrotik Traffic Monitor is a relatively small and lightweight server-side
tool to collect and process Accounting data from Mikrotik routers running RouterOS and
present them in a form that's easy to analyze.

It uses python Flask for the server side of things.

![](https://i.imgur.com/dLtKI4E.png)

# Installation

```bash
cd /opt/
git clone https://github.com/Nixellion/MikrotikTrafficMonitor.git
apt install python3 python3-pip python3-dev
cd MikrotikTrafficMonitor
pip3 install -r requirements.txt
cp MikrotikTrafficMonitor.service /lib/systemd/system
ssytemctl daemon-reload
systemctl enable MikrotikTrafficMonitor
service MikrotikTrafficMonitor start
systemctl status MikrotikTrafficMonitor
```

# Setting up Router

You need to go into IP - Accounting and enable Accounting, also enable Web Access and
type the IP of the machine where this tool will run on or leave it at default value.

You may also need to disable fast track as traffic that goes through fast track is not accounted for by RouterOS.