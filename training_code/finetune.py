from ultralytics import YOLO

model = YOLO('/home/yethu/Downloads/tmp/runs/detect/train30/weights/it30_best.pt')

results = model.train(data='data.yaml', epochs=100, imgsz=640, cache=True, plots=True, batch=0.6, classes=[0,1,2])
