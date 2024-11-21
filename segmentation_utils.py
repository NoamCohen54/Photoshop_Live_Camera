import torch
import numpy as np
from torchvision import models, transforms as T
from PIL import Image

# הגדרת מודל סגמנטציה (DeepLabV3)
segmentation_model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()

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

def composite_person_on_background(captured_image_path, background_image_path):
    person_img = Image.open(captured_image_path).convert("RGBA")
    background_img = Image.open(background_image_path).convert("RGBA")
    background_resized = background_img.resize(person_img.size, Image.LANCZOS)

    mask = get_segmentation_mask(person_img)
    mask_img = Image.fromarray(mask).convert("L").resize(person_img.size, Image.LANCZOS)

    final_image = Image.new("RGBA", person_img.size, (0, 0, 0, 0))
    final_image.paste(background_resized, (0, 0))
    person_image = Image.composite(person_img, Image.new("RGBA", person_img.size, (0, 0, 0, 0)), mask_img)
    final_image.paste(person_image, (0, 0), mask_img)

    final_image_path = f"{os.path.dirname(captured_image_path)}/final_image_with_bg.png"
    os.makedirs(os.path.dirname(final_image_path), exist_ok=True)
    final_image.save(final_image_path)
    return final_image_path
