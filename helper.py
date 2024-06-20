# Description: This file contains helper functions that are used in the main script.
import random


def cookie_process(cookie, headers):
    if not headers.get("Cookie"):
        headers["Cookie"] = cookie
        return cookie.split('msToken=')[1].split(';')[0]
    else:
        return headers["Cookie"].split('msToken=')[1].split(';')[0]


def generate_amz_time():
    import datetime
    amzdate = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    return amzdate


def split_pdf_into_images(file_path):
    # Export to High-Quality PPI 300
    import fitz
    import io
    from PIL import Image

    pdf = fitz.open(file_path)
    images = []
    for i in range(pdf.page_count):
        page = pdf[i]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        # Convert the PIL Image to bytes and append to the list
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()
        images.append(byte_arr)
    pdf.close()
    return images

def generate_local_message_id(length=21):
    import string
    # Define the characters that can be used to generate the id
    characters = string.ascii_letters + string.digits + '_-'
    # Generate a random string of the specified length
    local_message_id = ''.join(random.choice(characters) for _ in range(length))
    return local_message_id


def uuid_generator():
    import uuid
    return str(uuid.uuid4())


def randDID():
    import time
    return str(random.randint(0, 999999999) + int(time.time()))


def extract_text(text, start_delimiter, end_delimiter):
    try:
        return text.split(start_delimiter)[1].split(end_delimiter)[0]
    except IndexError:
        return None