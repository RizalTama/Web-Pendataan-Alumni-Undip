import os
import uuid
import re
from PIL import Image
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, subfolder, max_size=(800, 800)):
    """Save uploaded image, resize, and return filename."""
    if not file or not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)

    img = Image.open(file)
    img.thumbnail(max_size, Image.LANCZOS)

    # Convert RGBA to RGB if saving as JPEG
    if ext in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img.save(filepath)
    return filename


def delete_image(filename, subfolder):
    """Delete image file from disk if it exists."""
    if not filename:
        return
    filepath = os.path.join(current_app.root_path, 'static', 'uploads', subfolder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def page_range(page, total_pages, edge=1, around=2):
    """Windowed page numbers: first/last pages, pages around current,
    with None marking gaps (rendered as ellipsis)."""
    pages = []
    last = 0
    for p in range(1, total_pages + 1):
        if p <= edge or p > total_pages - edge or abs(p - page) <= around:
            if last and p - last > 1:
                pages.append(None)
            pages.append(p)
            last = p
    return pages


def paginate(query_result, page, per_page):
    """Paginate a list of results."""
    total = len(query_result)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    items = query_result[start:end]

    return {
        'data': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'page_range': page_range(page, total_pages),
    }
