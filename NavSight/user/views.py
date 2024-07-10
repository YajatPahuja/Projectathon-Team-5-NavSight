from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import base64
from io import BytesIO
import json
import cv2
import numpy as np
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration

# Create your views here.

model_yolo = YOLO("yolov9s.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"]

@csrf_exempt
def yolo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            image_data = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_data)).convert('RGB')
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            results = model_yolo(open_cv_image, stream=True, conf = 0.7)
            new_objects = set()
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    new_objects.add(classNames[cls])

            return JsonResponse({'new_objects': list(new_objects)})
        except Exception as e:
            print("Error:", str(e)) 
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'yolo.html')


processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

@csrf_exempt
def blip(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            image_data = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_data))

            inputs = processor(images=image, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)

            return JsonResponse({'caption': caption})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'blip.html')