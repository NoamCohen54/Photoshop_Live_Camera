import os
import base64
from PIL import Image
from io import BytesIO

# פונקציה לקבלת נתיב לתמונה על פי מונה מתעדכן
def get_image_path(image_counter):
    image_path = f"/content/History/image_{image_counter}/captured/webcam_image.jpg"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    return image_path

# פונקציה לשמירת תמונה מבסיס נתונים
def save_image_from_base64(base64_str, filename):
    img_data = base64.b64decode(base64_str.split(',')[1])
    image = Image.open(BytesIO(img_data))
    image.save(filename)
