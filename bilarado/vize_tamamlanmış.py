import cv2
import numpy as np
import time

def contour_merkezi(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    return None

def distance_between_points(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

video = cv2.VideoCapture('C:/Users/semih/Desktop/goruntu_isleme/vid_2.avi')
fps = video.get(cv2.CAP_PROP_FPS)
oyun_basladi = False
konum = {}
onceki_hiz = {'beyaz': 0, 'kirmizi': 0, 'sari': 0}
hareket_Ani = {'beyaz': 0, 'kirmizi': 0, 'sari': 0}
fps = video.get(cv2.CAP_PROP_FPS)
frame_counter = 0
frame_interval = 15  # Her 15 frame'de bir hız bilgisi yazdırılacak azaltıp artırabiliriz
merkezler = []  # Kırmızı topun merkez noktalarını saklamak için liste

ret, initial_frame = video.read()
if not ret:
    print("İlk frame alınamadı, video başlatılamıyor.")
else:
    h, w = initial_frame.shape[:2]
    path_image = np.zeros((h, w, 3), dtype=np.uint8)
    while True:
        ret, frame = video.read()
        if not ret:
            print("Video Sonlandı veya yüklenemedi.")
            break
     
        # Gauss bulanıklığı uygulayarak görüntüyü stabilize et
        frame = cv2.GaussianBlur(frame, (5, 5), 0) # diğer boyutlarla blur yapma denendi ve en iyi sonucu 5x5 vermiştir
        
    
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        beyaz_top = cv2.inRange(hsv, np.array([0, 0, 168]), np.array([172, 111, 255]))
        kirmizi_top = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
        sari_top = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))
    
        maskeler = {'beyaz': beyaz_top, 'kirmizi': kirmizi_top, 'sari': sari_top}
        
     
        toplar_stabil = True
        for renk, mask in maskeler.items():
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                buyuk_contour = max(contours, key=cv2.contourArea) 
                merkez = contour_merkezi(buyuk_contour)
                if merkez: #Sadece kırmızı top istenildiği için bunu koydum diğer toplarıda circle içine alınmak isterse bu blok kaldırılabilir
                    if renk =="kirmizi":
                        merkezler.append(merkez)
            
                        if len(merkezler) > 1:# Eğer merkezler listesinde birden fazla nokta varsa, çizgi çizebiliriz
                            for i in range(1, len(merkezler)): 
                                cv2.line(path_image, merkezler[i-1], merkezler[i], (0, 0, 255), 2)
                                #frame_counter ve i(merkez) değişkenlerini belirli aralıklarla kontrol ederek nesnenin hareketini takip eder ve her aralıkta gerçek nesne hızını hesaplar.
                                if (frame_counter % frame_interval == 0) and (i % frame_interval == 0):
                                    gercek_hiz = distance_between_points(merkezler[i-1], merkezler[i]) * fps
                                    hiz_metni = f"{gercek_hiz:.2f} px/s"
                                    metin_konumu = (merkezler[i][0] + 10, merkezler[i][1] + 10)
                                    cv2.putText(path_image, hiz_metni, metin_konumu, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
                        cv2.circle(frame, merkez, 5, (0, 255, 0), 2) 
                    
                    gercek_hiz = distance_between_points(konum.get(renk, merkez), merkez) * fps
                    if renk == 'kirmizi':  # Sadece kırmızı top istenildiği için bunu koydum  ama bütün topların hızı istenirse bu if koşulu kaldırılıp hepsini yazabiliriz
                        if gercek_hiz > 20:#video titremesinden dolayı burada böyle  bir sınırlayıcı koydum
                            cv2.putText(frame, f"{renk.capitalize()} top hizi: {gercek_hiz:.2f} px/s", (50, 20 + 30 * list(maskeler.keys()).index(renk)), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1)
                        else:
                            cv2.putText(frame, f"{renk.capitalize()} top hizi : 0 px/s", (50, 20 + 30 * list(maskeler.keys()).index(renk)), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0,255,255), 1)
                    if renk in konum and gercek_hiz > 0.5:
                        hareket_Ani[renk] += 1
                    else:
                        hareket_Ani[renk] = 0 
                    if hareket_Ani[renk] > 3:
                        toplar_stabil = False 
                        onceki_hiz[renk] = gercek_hiz
                    konum[renk] = merkez
    
    
        if oyun_basladi and toplar_stabil:
            #konsola anlık olarak diğer toplarında hızlarını print eden kod
            """for renk, gercek_hiz in onceki_hiz.items():
                print(f"{renk.capitalize()} top hizi:", gercek_hiz)"""
            if all(gercek_hiz < 28.284271247462 for gercek_hiz in onceki_hiz.values()):#28.284271247462 şeklide vermemin sebebi videodaki titremelerden dolayıdır
                başlama_mesaji2 = time.time()
    
                if oyun_basladi and time.time() - başlama_mesaji2 <= 2:
                    ekran_yüksekliği, ekran_genisligi = frame.shape[:2]
                    # sonladı yazısını ortalamak için yazılan kod
    
                    metin = "Oyun hamlesi bitti." 
                    font_olcek= 2
                    font_kalinlik = 2
                    font = cv2.FONT_HERSHEY_DUPLEX
                    metin_boyutu = cv2.getTextSize(metin, font, font_olcek, font_kalinlik)[0]
                    metin_genisligi, metin_yuksekligi = metin_boyutu[0], metin_boyutu[1]
                    metin_x = (ekran_genisligi - metin_genisligi) // 2
                    metin_y = (ekran_yüksekliği + metin_yuksekligi) // 2 + 80 
                    
                    cv2.putText(frame, metin, (metin_x, metin_y), font, font_olcek, (0,20,255), font_kalinlik)
    
        if not oyun_basladi and 'beyaz' in konum and hareket_Ani['beyaz'] > 5:#video da titreme olduğu için burada 5 verdim normalde 3'ün kullanılması planlamıştım
            oyun_basladi = True
            başlama_mesaji1 = time.time()
    
        if oyun_basladi and time.time() - başlama_mesaji1 <= 1:
            cv2.putText(frame, "Oyun Hamlesi yapildi.", (150, 450), cv2.FONT_HERSHEY_SIMPLEX , 0.9, (0,64,238), 2)
        frame_counter += 1
        cv2.imshow('oyun', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    cv2.imshow('Kirmizi Topun hareket Yolu ve Hizi', path_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
