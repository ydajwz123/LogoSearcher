import cv2
import numpy as np
import os

def canny(img):

    Canny_img = cv2.Canny(img, 50, 150)

    Gause_img = cv2.GaussianBlur(img, (3,3) ,0)

    img_sobel0 = np.float32(Gause_img)

    img_sobel = img_sobel0.copy()

    img_sobel1 = img_sobel0.copy()

    img_sobel2 = img_sobel0.copy()
    
    x = len(img_sobel)
    
    y = len(img_sobel[0])

    def sobel(img1, img2, img3, img4, x, y):
        for i in range(1, x-1):
            for j in range(1, y-1):
                gradx = img1[i+1][j-1] + 2*img1[i+1][j] + img1[i+1][j+1]\
                        - img1[i-1][j-1] - 2*img1[i-1][j] - img1[i-1][j+1]
                grady = img1[i-1][j+1] + 2*img1[i][j+1] + img1[i+1][j+1]\
                        - img1[i-1][j-1] - 2*img1[i][j-1] - img1[i+1][j-1]
                img3[i][j] = gradx
                img4[i][j] = grady
                img2[i][j] = np.sqrt(gradx*gradx + grady*grady) 
                
    sobel (img_sobel0, img_sobel, img_sobel1, img_sobel2, x, y)

    img_sobell = img_sobel.copy()

    for i in range(1, x-1):
        for j in range(1, y-1):
            if img_sobel1[i][j] != 0:
                tan = img_sobel2[i][j] / img_sobel1[i][j]
                if tan >= 0 and tan < 1:
                    dtmp1 = img_sobel[i-1][j]*(1-tan) + img_sobel[i-1][j-1]*tan
                    dtmp2 = img_sobel[i+1][j]*(1-tan) + img_sobel[i+1][j+1]*tan
                elif tan >= 1:
                    dtmp1 = img_sobel[i][j-1]*(1-1/tan) + img_sobel[i-1][j-1]/tan
                    dtmp2 = img_sobel[i][j+1]*(1-1/tan) + img_sobel[i+1][j+1]/tan
                elif tan <= -1:
                    dtmp1 = img_sobel[i][j-1]*(1+1/tan) - img_sobel[i+1][j-1]/tan
                    dtmp2 = img_sobel[i][j+1]*(1+1/tan) - img_sobel[i-1][j+1]/tan
                else:
                    dtmp1 = img_sobel[i-1][j]*(1+tan) - img_sobel[i-1][j+1]*tan
                    dtmp2 = img_sobel[i+1][j]*(1+tan) - img_sobel[i+1][j-1]*tan
            else:
                if img_sobel2[i][j] != 0:
                    dtmp1 = img_sobel[i][j-1]
                    dtmp2 = img_sobel[i][j+1]
                else:
                    dtmp1 = img_sobel[i-1][j-1]
                    dtmp2 = img_sobel[i+1][j+1]
            if img_sobel[i][j] >= dtmp1 and img_sobel[i][j] >= dtmp2:
                img_sobell[i][j] = 128
            else:
                img_sobell[i][j] = 0
    for i in range(0, x):
        img_sobell[i][0] = 0
        img_sobell[i][y-1] = 0
    for i in range(0, y):
        img_sobell[0][i] = 0
        img_sobell[x-1][i] = 0
    img_sobell1 = img_sobell.copy()
    img_sobell2 = img_sobell.copy()
    for i in range(1, x):
        for j in range(1, y):
            if img_sobel[i][j] >= 90 and img_sobell[i][j] == 128:
                img_sobell1[i][j] = 255
                img_sobell2[i][j] = 255
            elif img_sobel[i][j] >= 30 and img_sobell[i][j] == 128:
                img_sobell1[i][j] = 0
                img_sobell2[i][j] = 255
            elif img_sobell[i][j] == 128:
                img_sobell1[i][j] = 0
                img_sobell2[i][j] = 0
    img_sobell3 = img_sobell1.copy()

    def draw(img1, img2, x0, y0):
        for i in range(-1, 2):
            for j in range(-1,2):
                if img1[x0+i][y0+j] == 0 and img2[x0+i][y0+j] == 255:
                    if x0+i != 0 and x0+i != x-1 and y0+j != 0 and y0+j != y-1: 
                        img1[x0+i][y0+j] = 255
                        draw(img1, img2, x0+i, y0+j)
    
    for i in range(1, x-1):
        for j in range(1, y-1):
            if img_sobell1[i][j] == 255:
                draw(img_sobell3, img_sobell2, i, j)

    return img_sobell3
'''cv2.imwrite("canny_result3.jpg", Canny_img)
cv2.imwrite("my_result3.jpg", img_sobell3)
cv2.imshow("canny_result", Canny_img)
cv2.imshow("my_result", img_sobell3)
cv2.imshow("low", img_sobell1)
cv2.imshow("high", img_sobell2)
cv2.waitKey(0)
cv2.destroyAllWindows()'''

def hu(img):
    x = len(img)
    y = len(img[0])
    m10 = 0
    m01 = 0
    m00 = 0
    for i in range(0, x):
        for j in range(0, y):
            if img[i][j] != 0:
                m00 += img[i][j]
                m10 += img[i][j] * (i+1)
                m01 += img[i][j] * (j+1)
    xbar = m10 / m00
    ybar = m01 / m00
    u02 = 0
    u03 = 0
    u11 = 0
    u12 = 0
    u20 = 0
    u21 = 0
    u30 = 0
    for i in range(0, x):
        for j in range(0, y):
            if img[i][j] != 0:
                p = i + 1 - xbar
                q = j + 1 - ybar
                value = img[i][j]
                u02 += q * q * value
                u03 += q * q * q * value
                u11 += p * q * value
                u12 += p * q * q * value
                u20 += p * p * value
                u21 += p * p * q * value
                u30 += p * p * p * value
    u02 /= np.power(m00, 2)
    u03 /= np.power(m00, 2.5)
    u11 /= np.power(m00, 2)
    u12 /= np.power(m00, 2.5)
    u20 /= np.power(m00, 2)
    u21 /= np.power(m00, 2.5)
    u30 /= np.power(m00, 2.5)
    tmp1 = u20 - u02
    tmp2 = u30 - 3*u12
    tmp3 = u03 - 3*u21
    tmp4 = u30 + u12
    tmp5 = u03 + u21
    v1 = u20 + u02
    v2 = tmp1*tmp1 + 4*u11*u11
    v3 = tmp2*tmp2 + tmp3*tmp3
    v4 = tmp4*tmp4 + tmp5*tmp5
    v5 = tmp2*tmp4*(tmp4*tmp4-3*tmp5*tmp5) - tmp3*tmp5*(3*tmp4*tmp4- tmp5*tmp5)
    v6 = tmp1*(tmp4*tmp4-tmp5*tmp5) + 4*u11*tmp4*tmp5
    v7 = - tmp3*tmp4*(tmp4*tmp4-3*tmp5*tmp5) - tmp2*tmp5*(3*tmp4*tmp4-tmp5*tmp5)
    vec = [v1, v2, v3, v4, v5, v6, v7]
    lenvec = 0
    '''for i in range(0, 7):
        lenvec += vec[i] * vec[i]
    lenvec = np.sqrt(lenvec)
    for i in range(0, 7):
        vec[i] /= lenvec'''
    return vec

imgtar = cv2.imread('tt.jpg', cv2.IMREAD_GRAYSCALE)
imgtarca = canny(imgtar)
imgtarhu = hu(imgtarca)
mom = cv2.moments(imgtarca,True)
res = cv2.HuMoments(mom)
print res

def match(bian1, bian2):
    sim = 0
    for i in range(0, 7):
        a = np.log(np.absolute(bian1[i])) * np.sign(bian1[i])
        b = np.log(np.absolute(bian2[i])) * np.sign(bian2[i])
        sim += np.absolute((a-b)/b)
    return sim

img1 = cv2.imread('1.jpg', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('10.jpeg', cv2.IMREAD_GRAYSCALE)
img3 = cv2.imread('44.jpg', cv2.IMREAD_GRAYSCALE)
img4 = cv2.imread('5.jpg', cv2.IMREAD_GRAYSCALE)
img5 = cv2.imread('6.jpg', cv2.IMREAD_GRAYSCALE)
img6 = cv2.imread('7.jpg', cv2.IMREAD_GRAYSCALE)
img7 = cv2.imread('8.jpeg', cv2.IMREAD_GRAYSCALE)
img8 = cv2.imread('9.jpeg', cv2.IMREAD_GRAYSCALE)
img9 = cv2.imread('12.jpg', cv2.IMREAD_GRAYSCALE)
img10 = cv2.imread('11.jpg', cv2.IMREAD_GRAYSCALE)
img11 = cv2.imread('13.jpg', cv2.IMREAD_GRAYSCALE)
img12 = cv2.imread('14.jpg', cv2.IMREAD_GRAYSCALE)
print imgtarhu

imgli = [img1,img2,img3,img4,img5,img6,img7,img8,img9,img10,img11,img12]
for j in imgli:
    print match(imgtarhu, hu(canny(j)))
    #print hu(canny(j))
