from deepface import DeepFace
import matplotlib.pyplot as plt
import os

def detect_and_display_emotions(image_path):
    emotion_analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
    emotions = emotion_analysis[0]['emotion']
    predominant_emotion = max(emotions, key=emotions.get)

    # שמירת גרף הרגשות
    graph_path = f"{os.path.dirname(image_path)}/graphs/emotions_graph.png"
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

    return predominant_emotion
