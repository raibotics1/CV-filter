import cv2
import numpy as np

camera = cv2.VideoCapture(0)  # веб камера
cv2.namedWindow('settings',cv2.WINDOW_AUTOSIZE) # создаем окно настроек
if __name__ == '__main__':
    def nothing(*arg):
        pass


cv2.createTrackbar('h1', 'settings', 0, 255, nothing)
cv2.createTrackbar('s1', 'settings', 0, 255, nothing)
cv2.createTrackbar('v1', 'settings', 0, 255, nothing)
cv2.createTrackbar('h2', 'settings', 255, 255, nothing)
cv2.createTrackbar('s2', 'settings', 255, 255, nothing)
cv2.createTrackbar('v2', 'settings', 255, 255, nothing)

cv2.setTrackbarPos('h1', 'settings', 0)
cv2.setTrackbarPos('h2', 'settings', 185)
cv2.setTrackbarPos('s1', 'settings', 157)
cv2.setTrackbarPos('s2', 'settings', 237)
cv2.setTrackbarPos('v1', 'settings', 138)
cv2.setTrackbarPos('v2', 'settings', 255)




while True:
    iSee = False  # флаг: был ли найден контур
    controlX = 0.0  # нормализованное отклонение цветного объекта от центра кадра в диапазоне [-1; 1]
    controlY = 0.0
    success, frame = camera.read()  # читаем кадр с камеры


    if success:  # если прочитали успешно
        height, width = frame.shape[0:2]  # получаем разрешение кадра
        # считываем значения бегунков
        h1 = cv2.getTrackbarPos('h1', 'settings')
        s1 = cv2.getTrackbarPos('s1', 'settings')
        v1 = cv2.getTrackbarPos('v1', 'settings')
        h2 = cv2.getTrackbarPos('h2', 'settings')
        s2 = cv2.getTrackbarPos('s2', 'settings')
        v2 = cv2.getTrackbarPos('v2', 'settings')
        ## формируем начальный и конечный цвет фильтра
        h_min = np.array((h1, s1, v1), np.uint8)
        h_max = np.array((h2, s2, v2), np.uint8)
        # накладываем фильтр на кадр в модели HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
        binary = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))
        #binary = cv2.inRange(hsv, (113, 46, 35), (164,164, 255))  # пороговая обработка кадра (выделяем все желтое)
        # binary = cv2.inRange(hsv, (0, 0, 0), (255, 255, 35))  # пороговая обработка кадра (выделяем все черное)

        """
        # Чтобы выделить все красное необходимо произвести две пороговые обработки, т.к. тон красного цвета в hsv 
        # находится в начале и конце диапазона hue: [0; 180), а в openCV, хз почему, этот диапазон не закольцован.
        # поэтому выделяем красный цвет с одного и другого конца, а потом просто складываем обе битовые маски вместе

        
        """
        roi = cv2.bitwise_and(frame, frame,
                              mask=binary)  # за счет полученной маски можно выделить найденный объект из общего кадра

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей

        if len(contours) != 0:  # если найден хоть один контур
            maxc = max(contours, key=cv2.contourArea)  # находим наибольший контур
            moments = cv2.moments(maxc)  # получаем моменты этого контура
            """
            # moments["m00"] - нулевой момент соответствует площади контура в пикселях,
            # поэтому, если в битовой маске присутствуют шумы, можно вместо
            # if moments["m00"] != 0:  # использовать

            if moments["m00"] > 20: # тогда контуры с площадью меньше 20 пикселей не будут учитываться 
            """
            if moments["m00"] > 20:  # контуры с площадью меньше 20 пикселей не будут учитываться
                cx = int(moments["m10"] / moments["m00"])  # находим координаты центра контура (найденного объекта) по x
                cy = int(moments["m01"] / moments["m00"])  # находим координаты центра контура (найденного объекта) по y

                iSee = True  # устанавливаем флаг, что контур найден
                controlX = 2 * (
                            cx - width / 2) / width  # находим отклонение найденного объекта от центра кадра и нормализуем его (приводим к диапазону [-1; 1])
                controlY = -2 * (
                        cy - height / 2) / height
                cv2.drawContours(frame, maxc, -1, (0, 255, 0), 2)  # рисуем контур
                cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 2)  # рисуем линию линию по x
                cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 2)  # линия по y

        cv2.putText(frame, 'iSee: {};'.format(iSee), (width - 600, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # текст
        cv2.putText(frame, 'controlX: {:.2f}'.format(controlX), (width - 400, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)  # текст
        cv2.putText(frame, 'controlY: {:.2f}'.format(controlY), (width - 200, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)  # текст
        # cv2.circle(frame, (width//2, height//2), radius=4, color=(0, 0, 255), thickness=-1)    # центр кадра


        cv2.imshow('frame', frame)  # выводим все кадры на экран
        cv2.imshow('binary', binary)
        cv2.imshow('roi', roi)

    if cv2.waitKey(1) == ord('q'):  # чтоб выйти надо нажать 'q' на клавиатуре
        break

camera.release()
cv2.destroyAllWindows()
