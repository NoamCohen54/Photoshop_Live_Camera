from google.colab import output
from IPython.display import HTML, display
import base64
from PIL import Image
from io import BytesIO
import os
import torch
from diffusers import StableDiffusionPipeline
from torchvision import transforms as T, models
import numpy as np
import matplotlib.pyplot as plt
from deepface import DeepFace

# הגדרת נתיב בסיס ומודל Stable Diffusion
base_dir = "/content/History"
model_id = "stabilityai/stable-diffusion-2-1"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# הגדרת מודל סגמנטציה (DeepLabV3)
segmentation_model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()

# מונה תמונות
image_counter = 1

# פונקציה לקבלת נתיב לתמונה על פי מונה מתעדכן
def get_image_path():
    global image_counter
    image_path = f"{base_dir}/image_{image_counter}/captured/webcam_image.jpg"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image_counter += 1
    return image_path

# פונקציה להצגת ממשק המצלמה עם כפתורי הפעלה, עצירה ולכידה
def webcam_interface():
    display(HTML('''
        <style>
            /* עיצוב כללי של הדף */
            body {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
            }

            /* עיצוב המצלמה */
            video {
                width: 120px; /* רוחב המצלמה כך שיתאים לרוחב הכפתורים */
                height: 120px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
                object-fit: cover; /* ממלא את הקונטיינר בלי להשאיר רווחים (מניעת פס לבן) */
            }

            /* עיצוב שורת הכפתורים */
            .button-container {
                display: flex;
                justify-content: center;
                margin-top: 20px;
                gap: 0px; /* צמצום המרווח בין הכפתורים */
            }

            /* עיצוב כפתורים */
            button {
                width: 160px;
                height: 50px;
                font-size: 22px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }

            button:hover {
                background-color: #45a049;
            }

            /* עיצוב הודעת אזהרה */
            .glasses-warning {
                font-size: 24px;
                color: red;
                font-weight: bold;
                background-color: yellow;
                padding: 10px;
                border: 2px solid black;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 20px;
            }
            /* עיצוב הודעת אזהרה */
            .user-notification {
                font-size: 28px;
                color: red;
                font-weight: bold;
                background-color: black;
                padding: 10px;
                border: 2px solid black;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 20px;
            }

        </style>

        <div class="user-notification">תיתכן האפשרות שהרקע לא יהיה הכי דומה לרגש שזוהה</div>
        <div class="glasses-warning">שים לב! מומלץ להוריד משקפיים כדי לקבל תוצאה טובה יותר</div>

        <script>
            let videoElement;
            let canvasElement;
            let context;
            let videoStream;
            let inactivityTimeout;
            let secondInactivityTimeout;
            let cameraStarted = false;

            // פונקציה להפעלת המצלמה
            function startCamera() {
                if (!videoElement) {
                    videoElement = document.createElement('video');
                    videoElement.setAttribute('autoplay', '');
                    videoElement.setAttribute('playsinline', '');
                    videoElement.style.width = '480px'; /* רוחב התמונה */
                    videoElement.style.height = '480px'; /* גובה התמונה */
                    document.body.appendChild(videoElement);

                    canvasElement = document.createElement('canvas');
                    canvasElement.style.display = 'none';
                    context = canvasElement.getContext('2d');
                }

                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        videoStream = stream;
                        videoElement.srcObject = stream;
                        // הופך את התמונה למראה רגיל (לא הפוך)
                        videoElement.style.transform = 'scaleX(-1)';
                        resetInactivityTimer();
                    })
                    .catch(err => console.error('Error accessing webcam:', err));

                // הפעלת טיימרים לבדוק חוסר פעילות
                startInactivityTimers();
            }

            function stopCamera() {
                if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                }
                if (videoElement) {
                    videoElement.remove();
                    videoElement = null;
                }
                if (canvasElement) {
                    canvasElement.remove();
                    canvasElement = null;
                }

                clearInactivityTimers();
                alert("תודה שהשתמשת בי! מוזמן לחזור בכל עת 😊"); // הודעה כאשר עוצרים את המצלמה
            }

            function captureImage() {
                if (videoElement) {
                    canvasElement.width = videoElement.videoWidth;
                    canvasElement.height = videoElement.videoHeight;
                    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
                    const dataURL = canvasElement.toDataURL('image/jpeg');
                    google.colab.kernel.invokeFunction('notebook.capture_image', [dataURL], {});
                    resetInactivityTimer();
                } else {
                    alert('Camera is not active.');
                }
            }

            // יצירת כפתורים
            const startButton = document.createElement('button');
            startButton.innerText = 'Start Camera';
            startButton.onclick = startCamera;

            const stopButton = document.createElement('button');
            stopButton.innerText = 'Stop Camera';
            stopButton.onclick = stopCamera;

            const captureButton = document.createElement('button');
            captureButton.innerText = 'Capture Image';
            captureButton.onclick = captureImage;

            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('button-container');
            buttonContainer.appendChild(startButton);
            buttonContainer.appendChild(stopButton);
            buttonContainer.appendChild(captureButton);
            document.body.appendChild(buttonContainer);

            // הפעלת טיימרים לבדוק חוסר פעילות
            function startInactivityTimers() {
                inactivityTimeout = setTimeout(promptUserToContinue, 60000); // אחרי דקה
                secondInactivityTimeout = setTimeout(shutDownCamera, 120000); // אחרי שתי דקות
            }

            // איפוס טיימרים של חוסר פעילות
            function resetInactivityTimer() {
                clearInactivityTimers();
                startInactivityTimers();
            }

            // איפוס מלא של כל הטיימרים
            function clearInactivityTimers() {
                clearTimeout(inactivityTimeout);
                clearTimeout(secondInactivityTimeout);
            }

            // הצגת הודעה לאחר דקה של חוסר פעילות
            function promptUserToContinue() {
                const userResponse = confirm("האם אתה רוצה להמשיך להשתמש במצלמה?");
                if (userResponse) {
                    resetInactivityTimer();
                } else {
                    shutDownCamera();
                }
            }

            // כיבוי המצלמה אוטומטית אחרי שתי דקות
            function shutDownCamera() {
                stopCamera();
                alert("תודה שהשתמשת בי! מוזמן לחזור בכל עת 😊");
                
                setTimeout(function() {
                    const userResponse = confirm("האם תרצה להדליק את המצלמה שוב?");
                    if (userResponse) {
                        startCamera();
                    } else {
                        alert("תודה שהשתמשת בי! מוזמן לחזור בכל עת 😊");
                    }
                }, 90000); // אחרי 90 שניות
            }

            // הפעלת המצלמה אוטומטית כשמוצג הממשק
            startCamera(); // הוספתי את השורה הזאת להפעלת המצלמה אוטומטית
        </script>
    '''))

# פונקציה לשמירת תמונה מבסיס נתונים
def save_image_from_base64(base64_string):
    img_data = base64.b64decode(base64_string.split(',')[1])
    img = Image.open(BytesIO(img_data))
    img_path = get_image_path()
    img.save(img_path)
    print(f"Image saved as {img_path}")
    return img_path

# פונקציה לעיבוד רגשות בתמונה
def analyze_emotions(image_path):
    analysis = DeepFace.analyze(image_path, actions=['emotion'])
    return analysis

# הפעלת המצלמה והכפתורים
webcam_interface()
