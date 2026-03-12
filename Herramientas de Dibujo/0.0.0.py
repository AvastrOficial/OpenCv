import cv2
import numpy as np
import random
alto = 400
ancho = 600

lienzo = np.full((alto, ancho, 3), (130,130,130), dtype=np.uint8)

capa_nubes = np.zeros((alto, ancho, 3), dtype=np.uint8)

for _ in range(40):
    x = random.randint(0, ancho)
    y = random.randint(0, 200)
    radio = random.randint(30, 70)
    color = random.choice([(220,220,220), (255,255,255), (200,200,200)])
    cv2.circle(capa_nubes, (x, y), radio, color, -1)

capa_nubes = cv2.GaussianBlur(capa_nubes, (101,101), 0)

lienzo = cv2.addWeighted(lienzo, 1, capa_nubes, 0.6, 0)

cv2.rectangle(lienzo, (0, 330), (ancho, alto), (0,0,0), -1)

for x in range(0, ancho, 8):
    altura_random = random.randint(15, 35)
    cv2.line(lienzo,
             (x, 330),
             (x + random.randint(-3,3), 330 - altura_random),
             (0,0,0),
             2)

cv2.rectangle(lienzo, (260,260), (340,330), (0,0,255), -1)
cv2.rectangle(lienzo, (260,260), (340,330), (0,0,0), 3)

cv2.rectangle(lienzo, (285,230), (315,260), (160,160,160), -1)
cv2.rectangle(lienzo, (285,230), (315,260), (0,0,0), 3)

cv2.rectangle(lienzo, (200,150), (400,250), (0,0,255), -1)
cv2.rectangle(lienzo, (200,150), (400,250), (0,0,0), 4)

cv2.circle(lienzo, (240,200), 20, (0,255,255), -1)
cv2.circle(lienzo, (360,200), 20, (0,255,255), -1)
cv2.circle(lienzo, (240,200), 20, (0,0,0), 2)
cv2.circle(lienzo, (360,200), 20, (0,0,0), 2)

cv2.line(lienzo, (300,150), (300,110), (160,160,160), 5)
cv2.circle(lienzo, (300,100), 10, (160,160,160), -1)
cv2.circle(lienzo, (300,100), 10, (0,0,0), 2)

cv2.circle(lienzo, (230,290), 15, (0,0,255), -1)
cv2.circle(lienzo, (370,290), 15, (0,0,255), -1)
cv2.circle(lienzo, (230,290), 15, (0,0,0), 2)
cv2.circle(lienzo, (370,290), 15, (0,0,0), 2)

cv2.ellipse(lienzo, (280,350), (20,10), 0, 0, 360, (0,0,255), -1)
cv2.ellipse(lienzo, (320,350), (20,10), 0, 0, 360, (0,0,255), -1)
cv2.ellipse(lienzo, (280,350), (20,10), 0, 0, 360, (0,0,0), 2)
cv2.ellipse(lienzo, (320,350), (20,10), 0, 0, 360, (0,0,0), 2)

cv2.imshow("Robot Oscuro Mejorado", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()
