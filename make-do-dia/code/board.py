import cv2, numpy as np, sys
sys.path.insert(0, 'code'); from edl import EDL
cap = cv2.VideoCapture(sys.argv[1]); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
tiles = []; s = 0
for i, e in enumerate(EDL):
    n = int(e[2] * 15)
    for k, idx in enumerate((s + 1, s + n // 2, s + n - 2)):
        im = cv2.resize(frames[idx], (180, 320))
        if k == 0: cv2.putText(im, f'{i+1} {e[3]}', (4, 22), 0, 0.6, (0, 255, 255), 2)
        tiles.append(im)
    s += n
per = 24  # 8 clips x 3
for p in range(0, len(tiles), per):
    chunk = tiles[p:p+per]
    while len(chunk) < per: chunk.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(chunk[r*12:(r+1)*12]) for r in range(2)]
    cv2.imwrite(f'board_{p//per+1}.jpg', np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
print(len(frames), 'frames')
