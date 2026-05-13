import os
import io
import datetime
import argparse
import mimetypes
from flask import Flask, render_template_string, request, send_file, redirect, abort, jsonify
from cryptography.fernet import Fernet

# 🧩 Mechanics: Initialization & State
parser = argparse.ArgumentParser()
parser.add_argument("--upload", action="store_true", help="Enable global uploads")
args = parser.parse_args()

app = Flask(__name__)
RECORDINGS_DIR = os.getcwd()

server_state = {"uploads_enabled": args.upload}
ping_logs = {}
blacklisted_ips = set()
tools_state = {"clipboard": "", "chat": []}

# 🔐 Cryptography Engine (AES-128)
KEY_FILE = os.path.join(RECORDINGS_DIR, ".vault.key")
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as key_file: key_file.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as key_file: cipher_suite = Fernet(key_file.read())

# 📍 Security Gates
def is_admin():
    return request.remote_addr == '127.0.0.1'

@app.before_request
def sentinel_guard():
    ip = request.remote_addr
    if ip in blacklisted_ips and not is_admin(): abort(403)
    ping_logs[ip] = {"time": datetime.datetime.now().strftime("%H:%M:%S"), "path": request.path}

def get_directory_tree(path):
    tree = []
    try:
        for entry in os.scandir(path):
            if entry.name.startswith('.') or entry.name == "__pycache__": continue
            if entry.is_dir():
                tree.append({"type": "dir", "name": entry.name, "children": get_directory_tree(entry.path)})
            else:
                is_encrypted = entry.name.endswith(".enc")
                display_name = entry.name[:-4] if is_encrypted else entry.name
                tree.append({
                    "type": "file", "name": display_name, "real_name": entry.name,
                    "path": os.path.relpath(entry.path, RECORDINGS_DIR), "encrypted": is_encrypted
                })
    except Exception: pass
    return sorted(tree, key=lambda x: (x['type'] != 'dir', x['name'].lower()))

# 🎨 UI: Main Vault Layout
BASE_HTML = """
<!DOCTYPE html>
<html class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>SECURE_FS Vault</title>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
        details > summary { list-style: none; outline: none; }
        details > summary::-webkit-details-marker { display: none; }
        .floating-gh { position: fixed; bottom: 24px; right: 24px; z-index: 50; transition: all 0.3s; }
        .floating-gh:hover { transform: scale(1.15) rotate(-5deg); filter: drop-shadow(0 0 15px rgba(59,130,246,0.5)); }
    </style>
</head>
<body class="bg-[#09090b] text-zinc-100 font-sans h-screen flex flex-col overflow-hidden">
    
    <header class="h-14 border-b border-zinc-800 flex items-center justify-between px-6 bg-[#121214] z-30">
        <div class="flex items-center gap-6">
            <h1 class="text-blue-500 font-black text-xs tracking-[0.3em]">🛡️ SECURE_FS</h1>
            {% if is_admin %}
            <span class="text-[9px] bg-red-900/40 text-red-400 px-2 py-1 rounded font-bold uppercase tracking-widest border border-red-900/50">Admin Matrix</span>
            <form action="/admin/toggle_upload" method="post" class="ml-4 border-l border-zinc-800 pl-4">
                <button type="submit" class="text-[9px] px-3 py-1 rounded font-bold uppercase transition {% if uploads_enabled %}bg-emerald-600 hover:bg-emerald-500 text-white{% else %}bg-zinc-800 hover:bg-zinc-700 text-zinc-400{% endif %}">
                    {% if uploads_enabled %}Disable Uploads{% else %}Enable Uploads{% endif %}
                </button>
            </form>
            {% else %}
            <span class="text-[9px] bg-blue-900/20 text-blue-400 px-2 py-1 rounded font-bold uppercase tracking-widest border border-blue-900/30">Client Node</span>
            {% endif %}
            
            <div class="border-l border-zinc-800 pl-4 ml-2">
                <a href="/tools" target="preview-frame" class="text-[10px] bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 border border-indigo-500/30 px-4 py-1.5 rounded font-black uppercase tracking-widest transition flex items-center gap-2">
                    <span>⚡</span> SecOps Arsenal
                </a>
            </div>
        </div>
        <input type="text" id="fileSearch" placeholder="Search Vault..." class="bg-zinc-900 border border-zinc-800 rounded px-4 py-1.5 text-xs outline-none focus:border-blue-500 w-64 transition-all">
    </header>

    <div class="flex flex-1 overflow-hidden">
        <main class="flex-1 flex flex-col overflow-hidden relative">
            <div class="p-4 border-b border-zinc-800 flex justify-between items-center bg-[#0d0d0f]">
                <span class="text-[10px] text-zinc-500 font-black uppercase tracking-widest">Network File System</span>
                <div class="flex gap-2">
                    <button onclick="toggleTree(true)" class="text-[9px] bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 rounded transition font-bold text-zinc-300">Expand All</button>
                    <button onclick="toggleTree(false)" class="text-[9px] bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 rounded transition font-bold text-zinc-300">Shrink All</button>
                </div>
            </div>

            {% if uploads_enabled or is_admin %}
            <div class="p-4 border-b border-zinc-800/50 bg-zinc-900/20">
                <form action="/upload" method="post" enctype="multipart/form-data" class="max-w-2xl mx-auto flex items-center gap-4">
                    <input type="file" name="file" class="flex-1 text-xs text-zinc-400 file:bg-blue-600 file:hover:bg-blue-500 file:text-white file:border-0 file:rounded file:px-3 file:py-1.5 file:font-bold file:mr-4 file:transition cursor-pointer bg-zinc-950 border border-zinc-800 rounded p-1" required/>
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded text-xs font-bold uppercase tracking-widest transition shadow-lg shadow-blue-900/20 whitespace-nowrap">Secure Upload</button>
                </form>
            </div>
            {% endif %}

            <div class="flex-1 overflow-y-auto p-4 custom-scrollbar text-sm" id="treeContainer">
                {% macro render_tree(nodes) %}
                    {% for node in nodes %}
                        {% if node.type == 'dir' %}
                        <details class="tree-node ml-4 group mb-1">
                            <summary class="cursor-pointer p-1.5 rounded hover:bg-zinc-800/50 flex items-center gap-3 transition">
                                <span class="text-[10px] opacity-30 group-open:rotate-90 transition-transform">▶</span>
                                <span class="opacity-80 text-lg">📁</span><span class="font-medium text-zinc-300 group-hover:text-white">{{node.name}}</span>
                            </summary>
                            <div class="ml-5 border-l-2 border-zinc-800/50 pl-2 mt-1">{{ render_tree(node.children) }}</div>
                        </details>
                        {% else %}
                        <div class="file-item ml-10 py-1" data-name="{{ node.name.lower() }}">
                            <a href="/preview/{{node.real_name}}" target="preview-frame" class="flex items-center gap-3 p-1.5 rounded hover:bg-blue-900/20 hover:border-blue-500/30 border border-transparent transition group">
                                <span class="opacity-60 text-lg">{% if node.encrypted %}🔐{% else %}📄{% endif %}</span>
                                <span class="font-mono text-zinc-400 group-hover:text-blue-400 truncate">{{node.name}}</span>
                            </a>
                        </div>
                        {% endif %}
                    {% endfor %}
                {% endmacro %}
                {{ render_tree(tree) }}
            </div>
        </main>

        {% if is_admin %}
        <aside class="w-96 bg-[#121214] border-l border-zinc-800 flex flex-col shadow-2xl">
            <div class="p-4 bg-zinc-900/80 border-b border-zinc-800 flex justify-between items-center text-[10px]">
                <span class="text-red-500 font-black uppercase tracking-widest flex items-center gap-2"><span class="animate-pulse h-2 w-2 bg-red-500 rounded-full"></span> Telemetry</span>
                <span class="opacity-50 font-mono" id="ping-count">Nodes: {{ pings|length }}</span>
            </div>
            <div class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar" id="ping-sync">
                <div>
                    <h3 class="text-[9px] text-zinc-500 font-black uppercase tracking-widest mb-3 border-b border-zinc-800 pb-1">Network Activity</h3>
                    {% for ip, info in pings.items() %}
                    <div class="mb-2 p-2 rounded bg-zinc-900/50 border border-zinc-800/50">
                        <div class="flex justify-between items-start mb-1">
                            <span class="{% if ip == '127.0.0.1' %}text-blue-400{% else %}text-zinc-200{% endif %} font-mono text-[11px] font-bold">{{ ip }}</span>
                            <span class="text-zinc-600 text-[9px] font-mono">{{ info.time }}</span>
                        </div>
                        <div class="flex justify-between items-end">
                            <span class="text-[9px] text-zinc-500 truncate max-w-[180px]">{{ info.path }}</span>
                            {% if ip != '127.0.0.1' and ip not in blacklisted %}
                            <form action="/security/block/{{ ip }}" method="post"><button class="text-[9px] text-red-500 hover:text-red-400 font-bold bg-red-900/20 px-2 py-0.5 rounded border border-red-900/50">BLOCK</button></form>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% if blacklisted %}
                <div class="pt-4">
                    <h3 class="text-[9px] text-red-500 font-black uppercase tracking-widest mb-3 border-b border-red-900/30 pb-1">Banned Nodes</h3>
                    {% for b_ip in blacklisted %}
                    <div class="flex items-center justify-between p-2 rounded bg-red-900/10 border border-red-900/30 mb-2">
                        <span class="text-red-400 font-mono text-[10px] font-bold">{{ b_ip }}</span>
                        <form action="/security/unblock/{{ b_ip }}" method="post"><button class="text-[9px] text-zinc-400 hover:text-white font-bold bg-zinc-800 px-2 py-0.5 rounded">UNBLOCK</button></form>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </aside>
        {% endif %}
    </div>

    <a href="https://github.com/a0x14D" target="_blank" class="floating-gh bg-[#18181b] rounded-full shadow-2xl border border-zinc-800 p-2 group">
        <svg height="40" width="40" viewBox="0 0 16 16" fill="currentColor" class="text-zinc-400 group-hover:text-white transition-colors"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
    </a>

    <script>
        function toggleTree(expand) { document.querySelectorAll('.tree-node').forEach(node => node.open = expand); }
        const searchInput = document.getElementById('fileSearch');
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.file-item').forEach(item => {
                const match = item.getAttribute('data-name').includes(term);
                item.style.display = match ? 'block' : 'none';
                if (match && term.length > 0) {
                    let p = item.closest('details');
                    while (p) { p.open = true; p = p.parentElement.closest('details'); }
                }
            });
        });
        {% if is_admin %} setInterval(() => { location.reload(); }, 15000); {% endif %}
    </script>
</body>
</html>
"""

# 🎨 UI: SecOps Arsenal
TOOLS_HTML = """
<!DOCTYPE html>
<html class="dark">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <meta http-equiv="refresh" content="5">
</head>
<body class="bg-[#09090b] text-zinc-100 p-8 font-sans">
    <div class="max-w-6xl mx-auto space-y-6">
        <h1 class="text-2xl font-black text-indigo-400 tracking-tighter border-b border-zinc-800 pb-4">⚡ SecOps Arsenal & Community Hub</h1>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-6">
                <div class="bg-zinc-900/40 p-5 rounded-xl border border-zinc-800">
                    <h2 class="text-[10px] font-black uppercase text-zinc-500 mb-3 tracking-widest flex items-center gap-2">📋 Shared Clipboard</h2>
                    <form action="/tools/clip" method="post" class="space-y-3">
                        <textarea name="clipboard" rows="4" class="w-full bg-[#000] border border-zinc-800 rounded p-3 text-sm font-mono text-zinc-300 focus:border-indigo-500 outline-none">{{ clip }}</textarea>
                        <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-[10px] font-bold uppercase tracking-widest w-full">Sync to Network</button>
                    </form>
                </div>

                <div class="bg-zinc-900/40 p-5 rounded-xl border border-zinc-800 flex flex-col h-80">
                    <h2 class="text-[10px] font-black uppercase text-zinc-500 mb-3 tracking-widest flex items-center gap-2">💬 Node Comm-Link</h2>
                    <div class="flex-1 overflow-y-auto space-y-2 mb-3 pr-2 custom-scrollbar">
                        {% for msg in chat %}
                        <div class="p-2 bg-[#000] rounded border border-zinc-800/50">
                            <div class="flex justify-between items-baseline mb-1">
                                <span class="text-[10px] font-black {% if msg.ip == '127.0.0.1' %}text-red-400{% else %}text-indigo-400{% endif %}">{{ msg.ip }}</span>
                                <span class="text-[8px] text-zinc-600">{{ msg.time }}</span>
                            </div>
                            <p class="text-xs text-zinc-300 font-mono break-words">{{ msg.msg }}</p>
                        </div>
                        {% endfor %}
                    </div>
                    <form action="/tools/chat" method="post" class="flex gap-2">
                        <input name="msg" type="text" class="flex-1 bg-[#000] border border-zinc-800 rounded p-2 text-xs font-mono text-zinc-200 outline-none focus:border-indigo-500" placeholder="Broadcast message..." required autocomplete="off">
                        <button type="submit" class="bg-zinc-800 hover:bg-zinc-700 text-white px-4 rounded text-[10px] font-bold uppercase">Send</button>
                    </form>
                </div>
            </div>

            <div class="bg-zinc-900/40 p-5 rounded-xl border border-zinc-800">
                <h2 class="text-[10px] font-black uppercase text-zinc-500 mb-4 tracking-widest flex items-center gap-2">🧰 Local Toolkit (Client-Side)</h2>
                <div class="space-y-4">
                    <div class="bg-[#000] p-4 rounded border border-zinc-800/50">
                        <label class="text-[9px] uppercase font-bold text-zinc-500 block mb-2">Base64 Tool</label>
                        <textarea id="b64-input" rows="2" class="w-full bg-zinc-900 border border-zinc-800 rounded p-2 text-xs font-mono text-zinc-300 outline-none focus:border-indigo-500 mb-2" placeholder="Text here..."></textarea>
                        <div class="flex gap-2">
                            <button onclick="document.getElementById('b64-input').value = btoa(document.getElementById('b64-input').value)" class="flex-1 bg-zinc-800 hover:bg-zinc-700 py-1.5 rounded text-[10px] font-bold">Encode</button>
                            <button onclick="try{document.getElementById('b64-input').value = atob(document.getElementById('b64-input').value)}catch(e){alert('Invalid Base64')}" class="flex-1 bg-zinc-800 hover:bg-zinc-700 py-1.5 rounded text-[10px] font-bold">Decode</button>
                        </div>
                    </div>

                    <div class="bg-[#000] p-4 rounded border border-zinc-800/50">
                        <label class="text-[9px] uppercase font-bold text-zinc-500 block mb-2">SHA-256 Hash</label>
                        <input id="hash-input" type="text" class="w-full bg-zinc-900 border border-zinc-800 rounded p-2 text-xs font-mono text-zinc-300 outline-none focus:border-indigo-500 mb-2" placeholder="String..." oninput="generateHash()">
                        <div id="hash-output" class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-[10px] font-mono text-emerald-400 break-all select-all">Awaiting input...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        async function generateHash() {
            const input = document.getElementById('hash-input').value;
            if(!input) { document.getElementById('hash-output').innerText = 'Awaiting input...'; return; }
            const msgBuffer = new TextEncoder().encode(input);
            const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            document.getElementById('hash-output').innerText = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        }
    </script>
</body>
</html>
"""

# 🎨 UI: Syntax Highlighting
def render_code_preview(content, filename):
    return f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/tokyo-night-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            body {{ background: #09090b; color: #a9b1d6; margin: 0; padding: 20px; font-family: monospace; font-size: 14px; }}
            pre {{ margin: 0; border: 1px solid #27272a; border-radius: 8px; overflow: hidden; }}
            code {{ padding: 20px !important; }}
            .header {{ background: #121214; padding: 10px 20px; border-bottom: 1px solid #27272a; color: #52525b; font-weight: bold; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }}
        </style>
    </head>
    <body>
        <div class="header">Source View: {filename}</div>
        <pre><code class="language-plaintext">{content}</code></pre>
    </body>
    </html>
    """

# --- ROUTES ---

@app.route('/')
def index():
    return render_template_string(BASE_HTML, tree=get_directory_tree(RECORDINGS_DIR), pings=ping_logs, blacklisted=blacklisted_ips, uploads_enabled=server_state["uploads_enabled"], is_admin=is_admin())

@app.route('/admin/toggle_upload', methods=['POST'])
def toggle_upload():
    if is_admin(): server_state["uploads_enabled"] = not server_state["uploads_enabled"]
    return redirect('/')

@app.route('/security/block/<ip>', methods=['POST'])
def block_ip(ip):
    if is_admin(): blacklisted_ips.add(ip)
    return redirect('/')

@app.route('/security/unblock/<ip>', methods=['POST'])
def unblock_ip(ip):
    if is_admin() and ip in blacklisted_ips: blacklisted_ips.remove(ip)
    return redirect('/')

@app.route('/tools')
def tools_page():
    return render_template_string(TOOLS_HTML, clip=tools_state["clipboard"], chat=tools_state["chat"])

@app.route('/tools/clip', methods=['POST'])
def update_clip():
    tools_state["clipboard"] = request.form.get("clipboard", "")
    return redirect('/tools')

@app.route('/tools/chat', methods=['POST'])
def chat_post():
    msg = request.form.get("msg", "").strip()
    if msg:
        tools_state["chat"].append({"ip": request.remote_addr, "msg": msg, "time": datetime.datetime.now().strftime("%H:%M:%S")})
        if len(tools_state["chat"]) > 50: tools_state["chat"].pop(0)
    return redirect('/tools')

@app.route('/upload', methods=['POST'])
def upload_file():
    if not (is_admin() or server_state["uploads_enabled"]): abort(403)
    file = request.files.get('file')
    if file and file.filename:
        with open(os.path.join(RECORDINGS_DIR, file.filename + ".enc"), "wb") as f:
            f.write(cipher_suite.encrypt(file.read()))
    return redirect('/')

# 📍 INLINE PREVIEW FIX: Prevents "New Window/Download" behavior
@app.route('/preview/<path:filename>')
def preview_file(filename):
    file_path = os.path.join(RECORDINGS_DIR, filename)
    if not os.path.exists(file_path): abort(404)

    if filename.endswith(".enc"):
        with open(file_path, "rb") as f: decrypted_data = cipher_suite.decrypt(f.read())
        original_name = filename[:-4]
        
        if original_name.endswith(('.py', '.sh', '.txt', '.js', '.json', '.md', '.html')):
            return render_code_preview(decrypted_data.decode('utf-8', errors='ignore'), original_name)
            
        mime_type, _ = mimetypes.guess_type(original_name)
        return send_file(io.BytesIO(decrypted_data), mimetype=mime_type or 'application/octet-stream', as_attachment=False, download_name=original_name)
    
    if filename.endswith(('.py', '.sh', '.txt', '.js', '.json', '.md', '.html')):
        with open(file_path, "r", encoding='utf-8', errors='ignore') as f: return render_code_preview(f.read(), filename)

    mime_type, _ = mimetypes.guess_type(filename)
    return send_file(file_path, mimetype=mime_type, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
