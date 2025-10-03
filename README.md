Free File Converters — Complete Setup and Code
================================================

This repo contains a minimal, production-leaning file conversion service:

- Backend: FastAPI API that accepts uploads and converts using system tools
- Converters: ImageMagick (images), ffmpeg (audio/video), LibreOffice headless (docs→PDF)
- Frontend: simple upload UI at `public/convert.html`
- Docker: container with all tools preinstalled
- Nginx: example reverse proxy config


1) Requirements
----------------

- Linux host (Debian/Ubuntu recommended) or Docker
- For native run: `ffmpeg`, `imagemagick`, `libreoffice`, Python 3.11+
- For Docker run: Docker Engine


2) Run locally without Docker (quickest)
----------------------------------------

Install system tools:

```bash
sudo apt update && sudo apt install -y ffmpeg imagemagick libreoffice
```

Install Python deps and start API:

```bash
cd /workspace/server
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the frontend and test:

- Serve `public/` with any static server, e.g. VS Code Live Server, `python -m http.server` from `/workspace/public`, or your hosting.
- Ensure the frontend can reach the API:
  - Option A (recommended): Proxy `/convert` through Nginx to `http://localhost:8000/convert`
  - Option B: Edit `public/convert.html` and set `apiBase = "http://localhost:8000"`


3) Run with Docker (backend only)
---------------------------------

Build and run the API container:

```bash
cd /workspace/server
docker build -t freefileconverters:latest .
docker run --rm -p 8000:8000 --name ffc freefileconverters:latest
```

Then serve `public/` from any static server and point `/convert` to `http://localhost:8000/convert` (via Nginx or by setting `apiBase`).


4) Nginx example (static + proxy)
---------------------------------

Use `deploy/nginx.conf` as a template. Notes:

- Set `server_name` to your domain
- Mount or copy your built/static site to `/var/www/html`
- Point `proxy_pass` to your backend (container or host:port)

Reload Nginx after updating config:

```bash
sudo nginx -t && sudo systemctl reload nginx
```


5) Frontend usage
-----------------

- Open `/public/convert.html`
- Pick a file, choose a target format, click Convert
- The browser shows upload progress and downloads the converted file

Supported (demo):

- Images → any ImageMagick-supported format (png, jpg, webp, etc.)
- Audio/Video → any ffmpeg-supported format (mp3, mp4, etc.)
- Office docs (doc, docx, ppt, xls, od*) → PDF


6) Security and limits
----------------------

- Max size: 100 MB (see `server/app/main.py` `MAX_MB`)
- Randomized file names; outputs are served as downloads
- Timeouts on converter processes
- For production harden further: sandbox converters (e.g., Firejail/Docker), malware scan inputs (ClamAV), rate limiting, delete temp files regularly


7) Project layout
-----------------

```
/workspace
├─ public/
│  └─ convert.html          # Frontend upload page
├─ server/
│  ├─ app/main.py           # FastAPI API
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ .env.example
└─ deploy/
   └─ nginx.conf            # Example proxy config
```


8) Domain and HTTPS
-------------------

- Point DNS `A/AAAA` to your server/load balancer
- Use Let’s Encrypt (Certbot) or Cloudflare to enable TLS
- Increase `client_max_body_size` in Nginx for larger uploads


9) Extending
------------

- Add async jobs (Redis + RQ/Celery) for long-running conversions
- Add `pandoc` for markdown/latex; `ghostscript` for PDFs; `exiftool` for metadata
- Move storage to S3-compatible buckets and serve signed URLs


License
-------

Provided as-is. Use at your own risk.
