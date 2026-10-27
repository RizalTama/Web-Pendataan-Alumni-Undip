# ---------- build stage ----------
FROM python:3.12-slim AS builder

# Flask-MySQLdb menarik mysqlclient, dan mysqlclient tidak punya wheel manylinux
# sehingga harus dikompilasi. Compiler + header hanya hidup di stage ini dan
# tidak ikut ke image final.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ---------- runtime stage ----------
FROM python:3.12-slim

# libmariadb3 = pasangan runtime dari default-libmysqlclient-dev di atas.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmariadb3 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 alumni

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --chown=alumni:alumni . .

# Folder upload di-bind mount dari host; dibuat di sini supaya strukturnya sudah
# ada dan kepemilikannya benar sebelum upload pertama.
RUN mkdir -p /app/app/static/uploads/alumni \
             /app/app/static/uploads/news \
             /app/app/static/uploads/gallery \
    && chown -R alumni:alumni /app/app/static/uploads

USER alumni
EXPOSE 5005

# --preload meng-import run.py sekali di master process, jadi init_admin() jalan
# satu kali saja, bukan sekali per worker.
# gthread + 2 worker: app ini I/O-bound ke MySQL, thread lebih hemat RAM
# daripada menambah proses di VPS 2GB.
CMD ["gunicorn", "run:app", \
     "--bind", "0.0.0.0:5005", \
     "--worker-class", "gthread", \
     "--workers", "2", \
     "--threads", "4", \
     "--preload", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
