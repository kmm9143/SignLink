import pytest
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
from app import app
import base64
import io

client = TestClient(app)


# ===========================================================
# TC-US10-01 — Swap preprocessing (image)
# ===========================================================
def test_swap_preprocessing_image(monkeypatch):
    """Ensure cropping function can be swapped at runtime."""

    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(
        "routers.translate_image.init_hands",
        lambda static_image_mode=True: FakeHands()
    )

    def mock_crop(frame, hands):
        return np.zeros((224, 224, 3), dtype=np.uint8)

    monkeypatch.setattr(
        "routers.translate_image.crop_hand_from_frame",
        mock_crop
    )

    def mock_inference(_img):
        return {"predictions": [{"class": "A", "confidence": 0.99}]}

    monkeypatch.setattr(
        "routers.translate_image.run_asl_inference",
        mock_inference
    )

    with open("tests/test_data/ASL_A.png", "rb") as f:
        response = client.post(
            "/image/predict",
            files={"file": ("ASL_A.png", f, "image/png")}
        )

    assert response.status_code == 200
    data = response.json()

    assert data["predictions"][0]["class"] == "A"
    assert data["predictions"][0]["confidence"] >= 0.8


# ===========================================================
# TC-US10-02 — Swap inference backend (image)
# ===========================================================
def test_swap_inference_backend(monkeypatch):
    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(
        "routers.translate_image.init_hands",
        lambda static_image_mode=True: FakeHands()
    )

    monkeypatch.setattr(
        "routers.translate_image.crop_hand_from_frame",
        lambda f, h: np.zeros((224, 224, 3), dtype=np.uint8)
    )

    monkeypatch.setattr(
        "routers.translate_image.run_asl_inference",
        lambda _img: {"predictions": [{"class": "O", "confidence": 0.91}]}
    )

    with open("tests/test_data/ASL_O.png", "rb") as f:
        resp = client.post("/image/predict",
                           files={"file": ("ASL_O.png", f, "image/png")})

    assert resp.status_code == 200
    out = resp.json()

    assert out["predictions"][0]["class"] == "O"
    assert out["predictions"][0]["confidence"] >= 0.8

# ===========================================================
# TC-US10-02 — New model integration (fixed)
# ===========================================================
def test_new_model_integration(monkeypatch):
    import routers.translate_image as ti

    # --- Step 1: Create a mock "new model" inference ---
    def mock_new_model_inference(img_array):
        # Simulate the new model returning a unique prediction
        return {"predictions": [{"class": "A", "confidence": 0.97}]}

    # --- Step 2: Patch run_asl_inference to use the new model ---
    monkeypatch.setattr(ti, "run_asl_inference", mock_new_model_inference)

    # --- Step 3: Run the system using the new "model" ---
    with open("tests/test_data/ASL_A.png", "rb") as f:
        resp = client.post(
            "/image/predict",
            files={"file": ("ASL_A.png", f, "image/png")}
        )

    # --- Step 4: Verify the pipeline works with the new model ---
    assert resp.status_code == 200
    data = resp.json()
    assert "predictions" in data
    assert data["predictions"][0]["class"] == "A"
    assert data["predictions"][0]["confidence"] >= 0.9


# ===========================================================
# TC-US10-02 — New model integration for video
# ===========================================================
def test_new_model_integration_video(monkeypatch):
    import routers.translate_video as tv
    import numpy as np

    def mock_new_model_inference(img_array):
        return {"label": "B", "confidence": 0.96}

    monkeypatch.setattr(tv, "run_asl_inference", mock_new_model_inference)
    monkeypatch.setattr(tv, "crop_hand_from_frame",
                        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))
    monkeypatch.setattr(tv, "init_hands",
                        lambda static_image_mode=False: type(
                            "FakeHands", (), {"process": lambda self, rgb: type(
                                "FakeResults", (), {"multi_hand_landmarks": True})()})())

    with open("tests/test_data/ASL_Short_Video.mp4", "rb") as f:
        r_vid = client.post(
            "/video/translate",
            files={"file": ("ASL_Short_Video.mp4", f, "video/mp4")}
        )

    assert r_vid.status_code in (200, 422)
    if r_vid.status_code == 200:
        data = r_vid.json()
        # Check that every frame prediction has correct label/confidence
        for frame_pred in data["predictions"]:
            pred = frame_pred["prediction"]
            assert pred["label"] == "B"
            assert pred["confidence"] >= 0.9


# ===========================================================
# TC-US10-02 — New model integration for webcam
# ===========================================================
def test_new_model_integration_webcam(monkeypatch):
    import routers.translate_webcam as tw
    import base64
    import io
    from PIL import Image

    # --- Mock new model inference ---
    monkeypatch.setattr(tw, "run_asl_inference",
                        lambda img: {"label": "C", "confidence": 0.95})
    monkeypatch.setattr(tw, "crop_hand_from_frame",
                        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))

    # Build a test frame
    img = Image.new("RGB", (224, 224))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{encoded}"

    # Connect via websocket
    with client.websocket_connect("/webcam/ws") as ws:
        ws.send_text(data_url)
        ws.receive_bytes()   # frame bytes
        pred = ws.receive_json()

    assert pred["prediction"]["label"] == "C"
    assert pred["prediction"]["confidence"] >= 0.9


# ===========================================================
# TC-US10-03 — Modularity: components swappable (image)
# ===========================================================
def test_component_modularity(monkeypatch):
    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(
        "routers.translate_image.init_hands",
        lambda static_image_mode=True: FakeHands()
    )

    monkeypatch.setattr(
        "routers.translate_image.crop_hand_from_frame",
        lambda f, h: np.zeros((128, 128, 3), dtype=np.uint8)
    )

    monkeypatch.setattr(
        "routers.translate_image.run_asl_inference",
        lambda _img: {"predictions": [{"class": "V", "confidence": 0.93}]}
    )

    with open("tests/test_data/ASL_V.png", "rb") as f:
        resp = client.post("/image/predict",
                           files={"file": ("ASL_V.png", f, "image/png")})

    assert resp.status_code == 200
    out = resp.json()

    assert out["predictions"][0]["class"] == "V"
    assert out["predictions"][0]["confidence"] >= 0.8


# ===========================================================
# TC-US10-03 (extra) — New input mode using WEBCAM WS
# ===========================================================
def test_new_input_mode_mock_device(monkeypatch):
    import routers.translate_webcam as tw

    # --- Force crop to always return a valid image ---
    monkeypatch.setattr(
        tw,
        "crop_hand_from_frame",
        lambda *args, **kwargs: np.zeros((224, 224, 3), dtype=np.uint8)
    )

    # --- Fake inference backend ---
    monkeypatch.setattr(
        tw,
        "run_asl_inference",
        lambda *args, **kwargs: {"label": "A", "confidence": 0.95}
    )

    # Build base64 frame
    img = Image.new("RGB", (224, 224), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{encoded}"

    with client.websocket_connect("/webcam/ws") as ws:
        ws.send_text(data_url)

        frame_bytes = ws.receive_bytes()
        assert isinstance(frame_bytes, bytes)

        pred_json = ws.receive_json()

        assert pred_json["prediction"]["label"] == "A"
        assert pred_json["prediction"]["confidence"] >= 0.8


# ===========================================================
# TC-US10-04 — Bad crop = error (image)
# ===========================================================
def test_swap_bad_preprocessing(monkeypatch):
    import routers.translate_image as ti

    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(
        ti, "init_hands",
        lambda static_image_mode=True: FakeHands()
    )

    # bad crop
    monkeypatch.setattr(
        ti, "crop_hand_from_frame",
        lambda f, h: None
    )

    with open("tests/test_data/ASL_A.png", "rb") as f:
        resp = client.post("/image/predict",
                           files={"file": ("ASL_A.png", f, "image/png")})

    assert resp.status_code in (400, 422)


# ===========================================================
# TC-US10-04 — Regression: image + video + webcam still work
# ===========================================================
def test_image_translation(monkeypatch):
    import routers.translate_image as ti

    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(ti, "init_hands", lambda static_image_mode=True: FakeHands())
    monkeypatch.setattr(ti, "crop_hand_from_frame",
                        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))
    monkeypatch.setattr(ti, "run_asl_inference",
                        lambda img: {"predictions": [{"class": "A", "confidence": 0.92}]})

    with open("tests/test_data/ASL_A.png", "rb") as f:
        r_img = client.post(
            "/image/predict",
            files={"file": ("ASL_A.png", f, "image/png")}
        )
    assert r_img.status_code == 200
    data = r_img.json()
    assert data["predictions"][0]["class"] == "A"
    assert data["predictions"][0]["confidence"] >= 0.8

def test_video_translation(monkeypatch):
    import routers.translate_video as tv

    class FakeHands:
        def process(self, rgb):
            class FakeResults:
                multi_hand_landmarks = True
            return FakeResults()

    monkeypatch.setattr(tv, "init_hands", lambda static_image_mode=False: FakeHands())
    monkeypatch.setattr(tv, "crop_hand_from_frame",
                        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))
    monkeypatch.setattr(tv, "run_asl_inference",
                        lambda img: {"label": "A", "confidence": 0.92})

    with open("tests/test_data/ASL_Short_Video.mp4", "rb") as f:
        r_vid = client.post(
            "/video/translate",
            files={"file": ("ASL_Short_Video.mp4", f, "video/mp4")}
        )
    assert r_vid.status_code in (200, 422)

def test_webcam_translation(monkeypatch):
    import routers.translate_webcam as tw

    monkeypatch.setattr(tw, "crop_hand_from_frame",
                        lambda frame, hands: np.zeros((224, 224, 3), dtype=np.uint8))
    monkeypatch.setattr(tw, "run_asl_inference",
                        lambda img: {"label": "A", "confidence": 0.92})

    img = Image.new("RGB", (224, 224))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{encoded}"

    with client.websocket_connect("/webcam/ws") as ws:
        ws.send_text(data_url)
        ws.receive_bytes()   # frame bytes
        pred = ws.receive_json()

    assert pred["prediction"]["label"] == "A"
    assert pred["prediction"]["confidence"] >= 0.8
