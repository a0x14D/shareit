# ⚡️ **shareit** – Light‑weight File Sharing for Your Local Network

[![GitHub stars](https://img.shields.io/github/stars/a0x14D/shareit?style=for-the-badge)](https://github.com/a0x14D/shareit/stargazers)

[![GitHub forks](https://img.shields.io/github/forks/a0x14D/shareit?style=for-the-badge)](https://github.com/a0x14D/shareit/network)

[![GitHub issues](https://img.shields.io/github/issues/a0x14D/shareit?style=for-the-badge)](https://github.com/a0x14D/shareit/issues)  

> **Instantly share files and directories over your local network with a single command.**

---

## 📖  Overview

shareit is a tiny, **Python‑only** utility that temporarily spins up an HTTP server for the content you choose.  
It works on Linux, macOS and Windows (Python 3.7+ required). No external dependencies, no configuration – just run the script and copy‑paste the URL on any device connected to the same network.

Typical use‑cases:

* Transfer a photo from your phone to a laptop via Wi‑Fi.
* Make a config file available to a colleague in the same office.
* Quickly copy a folder to a backup machine without any set‑up.

---

## ✨  Features

🎯 **One‑liner** file / directory sharing 

 🌐  **Local‑network‑first**: The URL is only reachable from machines on the same subnet 

🔎 **Auto‑IP detection**: Shows your local IP and hostname 

 ⚡️  **Zero‑configuration**: No server hardening or port mapping needed 

 🛠  **Clean exit** on Ctrl‑C, logging, verbose mode 

 📦  **Python 3 only** – no compiled binaries, runs on any platform with Python installed 

---


## 🚀  Quick Start

### Prerequisites

* Python 3.7 or newer

### Installation

```bash

# Clone the repo
git clone https://github.com/a0x14D/shareit.git
cd shareit
```

> **Optional** – If you prefer to keep a single executable:

```bash

# Download the script directly
wget https://raw.githubusercontent.com/a0x14D/shareit/master/share.py

# Make it executable
chmod +x share.py
```

### Basic Share

```bash

# Share a single file
./share.py /path/to/photo.jpg

# Share an entire directory
./share.py /path/to/project/
```
```
Open that link on any device in the same network.
---

## 📦  Advanced Usage

```bash

# Show help
./share.py --help
```
> **Note** – The admin mode automatically grants full control to the local loopback (127.0.0.1). No external IP can access the admin CLI by default.
---

## 🤝  Contributing

We’re happy to accept contributions!

1. ✅ Fork the repo  
2. 🔧 Make your changes in a **feature branch**  
3. 🧪 Add (or improve) unit tests, documentation, or example scripts  
4. 💬 Submit a pull request – we’ll review it promptly
