import os
import torch
from deepface_utils import detect_and_display_emotions
from segmentation_utils import composite_person_on_background
from utils import webcam_interface

# הגדרת נתיב בסיס ומודל Stable Diffusion
base_dir = "/content/History"
model_id = "stabilityai/stable-diffusion-2-1"

# יצירת פייפליין ל- Stable Diffusion
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# הגדרת מודל סגמנטציה
segmentation_model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()

# הפעלת הממשק
webcam_interface()
