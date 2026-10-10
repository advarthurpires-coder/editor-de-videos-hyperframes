import cv2, numpy as np, sys, json
src, out, model = sys.argv[1], sys.argv[2], sys.argv[3]
cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS); W=int(cap.get(3)); H=int(cap.get(4))
det = cv2.FaceDetectorYN.create(model, '', (W, H), 0.6, 0.3, 5000)
step = 6  # 10 Hz at 60 fps
rows = []; i = 0
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        ok, f = cap.retrieve()
        _, faces = det.detect(f)
        if faces is not None and len(faces):
            fc = max(faces, key=lambda r: r[2]*r[3]*r[14])
            rows.append([i/fps, 1] + list(map(float, fc[:15])))
        else:
            rows.append([i/fps, 0] + [0]*15)
    i += 1
np.save(out, np.array(rows, dtype=np.float32))
a = np.array(rows); print(src, 'frames', len(a), 'hit%', round(100*a[:,1].mean(),1), 'W,H', W, H, 'fps', fps)
