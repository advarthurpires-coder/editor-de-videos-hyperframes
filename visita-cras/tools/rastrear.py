# Rastreia rosto (centro dos olhos, nariz, boca) e mãos (pulso, centro da palma, ponta do indicador)
# no vídeo do Arthur, quadro a quadro (30 fps), com MediaPipe Tasks. Saída: tools/rastreio.json
# Uso: python3 -I tools/rastrear.py src/arthur.mp4 tools/rastreio.json <pasta_modelos>
import sys, json, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, out, M = sys.argv[1:4]
face = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=f"{M}/face_landmarker.task"), running_mode=vision.RunningMode.VIDEO, num_faces=1))
hand = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=f"{M}/hand_landmarker.task"), running_mode=vision.RunningMode.VIDEO, num_hands=2,
    min_hand_detection_confidence=0.4, min_tracking_confidence=0.4))
cap = cv2.VideoCapture(src); W = cap.get(3); H = cap.get(4); fps = cap.get(5)
res = {"w": W, "h": H, "fps": fps, "f": []}; i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    ts = int(i * 1000 / fps)
    fa = face.detect_for_video(img, ts); ha = hand.detect_for_video(img, ts)
    d = {"t": round(i / fps, 3)}
    if fa.face_landmarks:
        L = fa.face_landmarks[0]
        P = lambda k: [round(L[k].x * W, 1), round(L[k].y * H, 1)]
        d["olhoE"], d["olhoD"], d["nariz"], d["boca"], d["queixo"], d["testa"] = P(33), P(263), P(1), P(13), P(152), P(10)
    hs = []
    for lm, hd in zip(ha.hand_landmarks, ha.handedness):
        P = lambda k: [round(lm[k].x * W, 1), round(lm[k].y * H, 1)]
        palma = [round(sum(lm[k].x for k in (0, 5, 9, 13, 17)) / 5 * W, 1), round(sum(lm[k].y for k in (0, 5, 9, 13, 17)) / 5 * H, 1)]
        # dedos estendidos (ponta mais longe do pulso que a articulação PIP)
        ext = []
        for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
            dt = (lm[tip].x - lm[0].x) ** 2 + (lm[tip].y - lm[0].y) ** 2
            dp = (lm[pip].x - lm[0].x) ** 2 + (lm[pip].y - lm[0].y) ** 2
            ext.append(int(dt > dp * 1.15))
        hs.append({"lado": hd[0].category_name, "conf": round(hd[0].score, 2), "pulso": P(0), "palma": palma, "indicador": P(8), "polegar": P(4), "dedos": ext})
    d["maos"] = hs
    res["f"].append(d); i += 1
json.dump(res, open(out, "w"), separators=(",", ":"))
print("quadros", i)
