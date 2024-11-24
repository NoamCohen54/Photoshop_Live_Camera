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
                font-size: 24px;
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
            }

            // הפעלת המצלמה אוטומטית כשמוצג הממשק
            startCamera(); // הוספתי את השורה הזאת להפעלת המצלמה אוטומטית
        </script>
    '''))

# פונקציה לשמירת תמונה מבסיס נתונים
def save_image_from_base64(base64_str, filename):
    img_data = base64.b64decode(base64_str.split(',')[1])
    image = Image.open(BytesIO(img_data))
    image.save(filename)

# פונקציה שמטפלת בתפיסת תמונה
def capture_image(base64_str):
    image_path = get_image_path()
    save_image_from_base64(base64_str, image_path)
    print(f"Image captured and saved as {image_path}")
    detect_and_display_emotions(image_path)

output.register_callback('notebook.capture_image', capture_image)

# פונקציות לעיבוד תמונה וסגמנטציה
def preprocess_image_for_segmentation(image):
    preprocess = T.Compose([
        T.Resize((520, 520)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return preprocess(image).unsqueeze(0)

def get_segmentation_mask(image):
    image_rgb = image.convert("RGB")
    input_tensor = preprocess_image_for_segmentation(image_rgb)
    with torch.no_grad():
        output = segmentation_model(input_tensor)['out'][0]
    output_predictions = output.argmax(0).byte().cpu().numpy()
    mask = np.where(output_predictions == 15, 255, 0).astype(np.uint8)
    return mask

# פונקציה לניתוח רגשות ושינוי רקע
def detect_and_display_emotions(image_path):
    emotion_analysis = DeepFace.analyze(image_path, actions=['emotion'])

    # הצגת גרף הרגשות
    emotions = emotion_analysis[0]['emotion']
    predominant_emotion = max(emotions, key=emotions.get)

    # שמירת גרף הרגשות
    graph_path = f"{base_dir}/image_{image_counter - 1}/graphs/emotions_graph.png"
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.bar(emotions.keys(), emotions.values(), color='blue')
    plt.xlabel('Emotions')
    plt.ylabel('Scores')
    plt.title('Emotion Analysis')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()

    print(f"Predominant Emotion: {predominant_emotion}")

    # יצירת רקע על סמך הרגש
    prompt = f"Create a background image that represents the feeling of {predominant_emotion}"
    result_image = pipe(prompt, num_inference_steps=50).images[0]

    # שמירת הרקע שנוצר
    background_image_path = f"{base_dir}/image_{image_counter - 1}/generated_background/background_{predominant_emotion}.png"
    os.makedirs(os.path.dirname(background_image_path), exist_ok=True)
    result_image.save(background_image_path)
    print(f"Generated background image saved as {background_image_path}")

    # שילוב הדמות על הרקע ושמירת התוצאה הסופית
    final_image_path = composite_person_on_background(image_path, background_image_path)
    print(f"Final image saved as {final_image_path}")

def composite_person_on_background(captured_image_path, background_image_path):
    # פתיחת התמונות שהתקבלו (תמונה של האדם והרקע)
    person_img = Image.open(captured_image_path).convert("RGBA")
    background_img = Image.open(background_image_path).convert("RGBA")

    # שינוי גודל הרקע כך שיתאים לגודל התמונה של האדם
    background_resized = background_img.resize(person_img.size, Image.LANCZOS)

    # יצירת מסכת סגמנטציה כדי להפריד את הדמות מהרקע
    mask = get_segmentation_mask(person_img)
    mask_img = Image.fromarray(mask).convert("L").resize(person_img.size, Image.LANCZOS)

    # יצירת התמונה המשולבת עם המסכה על הרקע
    person_with_mask = Image.composite(person_img, background_resized, mask_img)

    # שמירת התמונה המשותפת בנתיב הנכון
    final_image_path = f"{base_dir}/image_{image_counter - 1}/final_composite_image/final_composite_image.png"

    # יצירת תיקייה אם לא קיימת והצלת התמונה
    os.makedirs(os.path.dirname(final_image_path), exist_ok=True)
    person_with_mask.save(final_image_path)

    # החזרת נתיב התמונה הסופית
    return final_image_path


# הצגת ממשק המצלמה
webcam_interface()
