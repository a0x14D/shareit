<div align="center">

# 🛡️ SECURE_FS Vault (shareit)

**Instantly share files and directories over your local network with a single command.**

[![GitHub stars](https://img.shields.io/github/stars/a0x14D/shareit?style=for-the-badge&color=3b82f6)](https://github.com/a0x14D/shareit/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/a0x14D/shareit?style=for-the-badge&color=3b82f6)](https://github.com/a0x14D/shareit/network)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

---

## 📖 Overview

**SECURE_FS Vault** (formerly *shareit*) is a powerful, elegant, single-file Python utility that spins up an instant file-sharing server for your local network. It works flawlessly on Linux, macOS, and Windows.

With its dark glassmorphism interface, it feels premium while remaining incredibly lightweight. No configuration, no messy dependencies—just run it and start sharing.

---

## ✨ Key Features

### 🎨 Beautiful & Responsive UI
- **Dark Glassmorphism Design:** Modern aesthetic with frosted panels, Inter typography, and micro-animations.
- **Split-Pane Architecture:** Persistent file tree on the left, seamless inline file preview on the right.
- **Mobile Friendly:** Fully responsive for viewing on phones or tablets.

### ⚡ Seamless Sharing & "Everyday" Tools
- **Drag & Drop Uploads:** Just drag files onto the UI to securely upload them (if enabled).
- **QR Code Pairing:** Instantly beam the URL to your phone via the built-in client-side QR generator.
- **Folder ZIP Downloads:** Click the 📦 icon next to any folder to instantly compress and download the entire directory.
- **File Deletion:** Authorized nodes can delete files straight from the tree view.
- **Markdown & Code Previews:** Beautifully renders `.md` files and syntax-highlights source code directly in the browser.
- **Native Media Viewers:** Wraps images, `<video>`, and `<audio>` files in centered, dark-themed players rather than relying on unstyled browser defaults.

### 🛡️ SecOps Arsenal & Security Hardenings
- **Admin Matrix:** Real-time telemetry showing connected nodes and network activity.
- **Path Traversal Protection:** Hardened backend utilizing `os.path.realpath` to prevent directory escape attacks.
- **XSS Mitigations:** All code previews are strictly `html.escaped`, and markdown rendering uses `DOMPurify` to sanitize HTML output, preventing Cross-Site Scripting.
- **Built-in Toolkit:** Includes client-side Base64 encoding, SHA-256 hashing, JSON formatting, and Password Generation.

---

## 🚀 Quick Start

### Prerequisites
* Python 3.7 or newer
* Flask & Cryptography (`pip install flask cryptography werkzeug`)

### Installation

```bash
# Clone the repository
git clone https://github.com/a0x14D/shareit.git
cd shareit

# Make it executable
chmod +x share
```

### Usage

Run the server in the directory you want to share:

```bash
# Start the vault (sharing current directory)
./share

# Start the vault and enable global uploads from any device
./share --upload
```

Once running, simply open the provided `http://<your-ip>:8000` link on any device in your network.

---

## 🛠️ Advanced Tools

The **SecOps Arsenal** is accessible via the `⚡ SecOps Arsenal` button in the UI. It provides:
- **Node Comm-Link:** A real-time chat room for all connected devices.
- **Shared Clipboard:** Instantly sync text snippets across devices.
- **Utility Toolkit:** Base64, URL Encoding, JSON minification, and more—all running instantly in the browser.

---

## 🤝 Contributing

We welcome contributions to make SECURE_FS even better!

1. ✅ Fork the repo
2. 🔧 Make your changes in a feature branch
3. 💬 Submit a pull request—we’ll review it promptly

<div align="center">
  <sub>Built with ❤️ for secure, effortless local sharing.</sub>
</div>
