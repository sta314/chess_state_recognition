import torch
import cv2

def load_yolo_model(weights_path, local = False):
    print("-----------------------")
    print("Loading YOLOv5 model...")
    print("-----------------------")
    if local:
        return torch.hub.load("../yolov5", "custom", source = "local", path = weights_path, force_reload = False)
    else:
        return torch.hub.load("ultralytics/yolov5", "custom", path = weights_path, force_reload = False)

def predict_image(img_to_predict, model):
    prediction = model(cv2.cvtColor(img_to_predict, cv2.COLOR_BGR2RGB))
    model_output = prediction.xyxyn[0].cpu().numpy()

    return model_output