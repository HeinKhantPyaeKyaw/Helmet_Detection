from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("yolo11n.pt")

#results = model.train(data="data.yaml", epochs=200, imgsz=640, cache=True, plots=True, bgr=0.5, scale=0.0, perspective=0.001, mixup=0.5, copy_paste=0.5, erasing=0.5, crop_fraction=0.1, save_crop=True, workers=12, optimizer='Adam', flipud=0.5, dropout=0.1, batch=0.8, classes=[0,1,2])
results = model.train(data="data.yaml", epochs=300, imgsz=640, cache=True, plots=True, batch=0.6, classes=[0,1,2])
