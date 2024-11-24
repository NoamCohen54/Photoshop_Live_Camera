# Photoshop_Live_Camera Emotion-Based Background Generation with Stable Diffusion
This project uses the Stable Diffusion model, along with DeepFace and a webcam interface, to generate and save images based on detected emotions from real-time video input.

## Overview
This code creates a live webcam interface where users can capture their image, which is then analyzed for emotions. Based on the detected emotion, a relevant background or effect is applied using Stable Diffusion. It also provides a notification to improve capture quality by advising users to remove glasses.

## How It Works
1. **Emotion Analysis**: The captured image is analyzed using DeepFace to detect emotions.
2. **Background Generation**: Based on the detected emotion, the Stable Diffusion model generates an image that aligns with that emotion.
3. **Image Saving**: Each generated image, along with the captured webcam image, is saved in a uniquely indexed directory under `/content/History`.
4. **Webcam Interface**: The code includes a dynamic HTML and JavaScript interface for starting/stopping the camera and capturing images, with inactivity timers to help control webcam usage.

## Features
- **GPU/CPU Detection**: The program automatically uses a GPU if available; otherwise, it defaults to the CPU.
- **Emotion-Based Backgrounds**: Generates backgrounds or visual effects based on detected emotions using Stable Diffusion.
- **Image and Prompt History**: Each generated image and emotion analysis is saved in a structured folder system.
- **User Notifications**: On-screen notifications suggest removing glasses for better detection accuracy and warn that backgrounds may not fully reflect detected emotions.

## Using the Webcam Interface
1. **Start the Camera**: Press the **Start Camera** button to begin.
2. **Capture Image**: Once ready, press **Capture Image** to take a photo and analyze its emotions.
3. **Stop the Camera**: Press **Stop Camera** to end the webcam session.
4. **Inactivity Alerts**: After 1 minute of inactivity, you’ll be asked if you want to continue. After 2 minutes, the camera will stop automatically.

## Directory Structure
- **/content/History/image_***: Each captured image and generated background are saved in a unique subfolder, with the original image saved as `webcam_image.jpg`.

## Requirements
Install the necessary libraries with:
```bash
pip install diffusers transformers torch torchvision deepface
