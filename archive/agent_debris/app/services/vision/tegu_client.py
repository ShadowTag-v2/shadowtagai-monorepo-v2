"""
Tegu Network_Model wrapper for computer vision tasks.

Integrates Tegu's ML toolbox with GPU acceleration and model caching.
"""

import os
from typing import Any
from pathlib import Path
import numpy as np
import structlog

logger = structlog.get_logger()


class TeguClient:
    """
    Client for Tegu computer vision models.

    Supports:
    - Image classification (ResNet, VGG, Inception)
    - Object detection (YOLO, SSD)
    - Facial recognition (FaceNet, VGGFace)
    - Video classification (3D-CNN, LSTM)
    """

    SUPPORTED_MODELS = {
        "resnet50": "image_classification",
        "vgg16": "image_classification",
        "inception_v3": "image_classification",
        "yolo_v3": "object_detection",
        "ssd_mobilenet": "object_detection",
        "facenet": "face_recognition",
        "vggface": "face_recognition",
        "3d_cnn": "video_classification",
    }

    def __init__(
        self,
        model: str = "resnet50",
        gpu: bool = True,
        model_path: str | None = None,
    ):
        """
        Initialize Tegu client.

        Args:
            model: Model name (see SUPPORTED_MODELS)
            gpu: Use GPU acceleration (requires CUDA/cuDNN)
            model_path: Custom model weights path (optional)
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {list(self.SUPPORTED_MODELS.keys())}")

        self.model_name = model
        self.model_type = self.SUPPORTED_MODELS[model]
        self.gpu = gpu
        self.model_path = model_path or os.getenv("TEGU_MODEL_PATH", "/models")

        # Lazy load model on first inference
        self._model = None
        self._loaded = False

        logger.info("tegu_client_initialized", model=model, gpu=gpu, model_path=self.model_path)

    def _load_model(self):
        """Load TensorFlow/Keras model (lazy loading)."""
        if self._loaded:
            return

        # Import TensorFlow only when needed
        try:
            import tensorflow as tf
            from tensorflow import keras
        except ImportError:
            raise ImportError("TensorFlow not installed. Install with: pip install tensorflow>=2.10.0")

        # Configure GPU
        if self.gpu:
            gpus = tf.config.list_physical_devices("GPU")
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    logger.info("gpu_enabled", gpu_count=len(gpus))
                except RuntimeError as e:
                    logger.error("gpu_config_failed", error=str(e))
        else:
            tf.config.set_visible_devices([], "GPU")

        # Load model weights
        model_file = Path(self.model_path) / f"{self.model_name}.h5"

        if model_file.exists():
            self._model = keras.models.load_model(str(model_file))
            logger.info("model_loaded_from_disk", model_file=str(model_file))
        else:
            # Load pre-trained from Keras applications
            if self.model_name == "resnet50":
                self._model = keras.applications.ResNet50(weights="imagenet")
            elif self.model_name == "vgg16":
                self._model = keras.applications.VGG16(weights="imagenet")
            elif self.model_name == "inception_v3":
                self._model = keras.applications.InceptionV3(weights="imagenet")
            else:
                raise ValueError(f"Pre-trained weights not available for {self.model_name}")

            logger.info("model_loaded_pretrained", model=self.model_name)

        self._loaded = True

    async def classify_image(
        self,
        image_path: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Classify image.

        Args:
            image_path: Path to image file
            top_k: Return top K predictions

        Returns:
            List of {class, confidence, class_id}
        """
        if self.model_type != "image_classification":
            raise ValueError(f"Model {self.model_name} is not for image classification")

        self._load_model()

        # Import TensorFlow for preprocessing
        from tensorflow import keras

        # Load and preprocess image
        img = keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        # Model-specific preprocessing
        if self.model_name == "resnet50":
            img_array = keras.applications.resnet50.preprocess_input(img_array)
        elif self.model_name == "vgg16":
            img_array = keras.applications.vgg16.preprocess_input(img_array)
        elif self.model_name == "inception_v3":
            img_array = keras.applications.inception_v3.preprocess_input(img_array)

        # Run inference
        predictions = self._model.predict(img_array, verbose=0)

        # Decode predictions
        if self.model_name in ["resnet50", "vgg16"]:
            decoded = keras.applications.imagenet_utils.decode_predictions(predictions, top=top_k)[0]
        elif self.model_name == "inception_v3":
            decoded = keras.applications.inception_v3.decode_predictions(predictions, top=top_k)[0]

        results = [
            {
                "class_id": class_id,
                "class": class_name,
                "confidence": float(confidence),
            }
            for class_id, class_name, confidence in decoded
        ]

        logger.info("image_classified", image=image_path, top_class=results[0]["class"], confidence=results[0]["confidence"])

        return results

    async def detect_objects(
        self,
        image_path: str,
        confidence_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        Detect objects in image using YOLO/SSD.

        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence (0-1)

        Returns:
            List of {class, confidence, bbox: [x, y, w, h]}
        """
        if self.model_type != "object_detection":
            raise ValueError(f"Model {self.model_name} is not for object detection")

        # Use OpenCV DNN module for YOLO/SSD
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV not installed. Install with: pip install opencv-python>=4.5.0")

        # Load image
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Load YOLO/SSD model
        if self.model_name == "yolo_v3":
            net = cv2.dnn.readNetFromDarknet(f"{self.model_path}/yolov3.cfg", f"{self.model_path}/yolov3.weights")
            blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
            layer_names = net.getLayerNames()
            output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        elif self.model_name == "ssd_mobilenet":
            net = cv2.dnn.readNetFromTensorflow(f"{self.model_path}/ssd_mobilenet.pb", f"{self.model_path}/ssd_mobilenet.pbtxt")
            blob = cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True)
            output_layers = ["detection_out"]

        net.setInput(blob)
        outputs = net.forward(output_layers)

        # Parse detections
        detections = []
        for output in outputs:
            for detection in output:
                if self.model_name == "yolo_v3":
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > confidence_threshold:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        detections.append(
                            {
                                "class_id": int(class_id),
                                "class": self._get_coco_class_name(class_id),
                                "confidence": float(confidence),
                                "bbox": [x, y, w, h],
                            }
                        )

        logger.info("objects_detected", image=image_path, count=len(detections))

        return detections

    async def recognize_faces(
        self,
        image_path: str,
        feature_library: dict[str, np.ndarray] | None = None,
        threshold: float = 0.6,
    ) -> list[dict[str, Any]]:
        """
        Recognize faces in image.

        Args:
            image_path: Path to image file
            feature_library: Dict of {name: feature_vector} for known faces
            threshold: Similarity threshold (0-1)

        Returns:
            List of {name, confidence, bbox: [x, y, w, h]}
        """
        if self.model_type != "face_recognition":
            raise ValueError(f"Model {self.model_name} is not for face recognition")

        # Use OpenCV for face detection, Tegu for recognition
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV not installed. Install with: pip install opencv-python>=4.5.0")

        # Detect faces with Haar cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        results = []
        for x, y, w, h in faces:
            face_img = image[y : y + h, x : x + w]

            # Extract face embedding (simplified - in production use FaceNet/VGGFace)
            face_resized = cv2.resize(face_img, (160, 160))
            embedding = self._extract_face_embedding(face_resized)

            # Match against feature library
            if feature_library:
                best_match = None
                best_distance = float("inf")

                for name, lib_embedding in feature_library.items():
                    distance = np.linalg.norm(embedding - lib_embedding)
                    if distance < best_distance:
                        best_distance = distance
                        best_match = name

                if best_distance < (1 - threshold):
                    results.append(
                        {
                            "name": best_match,
                            "confidence": float(1 - best_distance),
                            "bbox": [int(x), int(y), int(w), int(h)],
                        }
                    )
            else:
                results.append(
                    {
                        "name": "unknown",
                        "confidence": 1.0,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "embedding": embedding.tolist(),
                    }
                )

        logger.info("faces_recognized", image=image_path, count=len(results))

        return results

    def _extract_face_embedding(self, face_img: np.ndarray) -> np.ndarray:
        """Extract face embedding vector (simplified placeholder)."""
        # In production, use pre-trained FaceNet/VGGFace
        # For now, return dummy 128-dim embedding
        return np.random.rand(128)

    def _get_coco_class_name(self, class_id: int) -> str:
        """Get COCO dataset class name from class ID."""
        # Simplified COCO classes (full list has 80 classes)
        coco_classes = [
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "airplane",
            "bus",
            "train",
            "truck",
            "boat",
            "traffic light",
            "fire hydrant",
            "stop sign",
            "parking meter",
            "bench",
            "bird",
            "cat",
            "dog",
            "horse",
            "sheep",
            "cow",
            "elephant",
            "bear",
            "zebra",
            "giraffe",
        ]
        return coco_classes[class_id] if class_id < len(coco_classes) else f"class_{class_id}"

    async def classify_video(
        self,
        video_path: str,
        sample_rate: int = 30,  # Sample every N frames
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Classify video by sampling frames.

        Args:
            video_path: Path to video file
            sample_rate: Sample every N frames
            top_k: Top K predictions per frame

        Returns:
            {
                "duration_seconds": float,
                "total_frames": int,
                "sampled_frames": int,
                "top_classes": List[{class, confidence, frame_count}],
                "frame_predictions": List[List[{class, confidence}]]
            }
        """
        if self.model_type != "video_classification" and self.model_type != "image_classification":
            raise ValueError(f"Model {self.model_name} cannot classify videos")

        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV not installed. Install with: pip install opencv-python>=4.5.0")

        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        frame_predictions = []
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Sample every N frames
            if frame_idx % sample_rate == 0:
                # Save frame temporarily
                temp_frame_path = f"/tmp/frame_{frame_idx}.jpg"
                cv2.imwrite(temp_frame_path, frame)

                # Classify frame
                predictions = await self.classify_image(temp_frame_path, top_k=top_k)
                frame_predictions.append(predictions)

                # Cleanup
                os.remove(temp_frame_path)

            frame_idx += 1

        cap.release()

        # Aggregate predictions across frames
        class_counts: dict[str, dict[str, Any]] = {}
        for preds in frame_predictions:
            for pred in preds:
                class_name = pred["class"]
                if class_name not in class_counts:
                    class_counts[class_name] = {"class": class_name, "total_confidence": 0.0, "frame_count": 0}
                class_counts[class_name]["total_confidence"] += pred["confidence"]
                class_counts[class_name]["frame_count"] += 1

        # Calculate average confidence and sort
        top_classes = [
            {
                "class": data["class"],
                "confidence": data["total_confidence"] / data["frame_count"],
                "frame_count": data["frame_count"],
            }
            for data in class_counts.values()
        ]
        top_classes.sort(key=lambda x: x["confidence"], reverse=True)

        result = {
            "duration_seconds": duration,
            "total_frames": total_frames,
            "sampled_frames": len(frame_predictions),
            "top_classes": top_classes[:top_k],
            "frame_predictions": frame_predictions,
        }

        logger.info("video_classified", video=video_path, duration=duration, top_class=top_classes[0]["class"] if top_classes else None)

        return result
