import os
from os.path import join
import subprocess
import sys
import cv2
import numpy as np


def pretty_blur_map(blur_map: np.array, sigma: int = 5, min_abs: float = 0.5):
    abs_image = np.abs(blur_map).astype(np.float32)
    abs_image[abs_image < min_abs] = min_abs

    abs_image = np.log(abs_image)
    cv2.blur(abs_image, (sigma, sigma))
    return cv2.medianBlur(abs_image, sigma)


def detect_blur(image_path, expected_pixels=2E6):
    image = cv2.imread(str(image_path))
    if not image is None:
        # resize image as blur detector is highly resolution-dependent
        ratio = np.sqrt(expected_pixels / (image.shape[0] * image.shape[1]))
        img = cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
        
        if image.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        blur_map = cv2.Laplacian(img, cv2.CV_64F)
        score = np.var(blur_map)
        #blur_map, score, bool(score < threshold)

        if 0:
            cv2.imshow('input', image)
            cv2.imshow('result', pretty_blur_map(blur_map))

            if cv2.waitKey(0) == ord('q'):
                logging.info('exiting...')
                exit()
        
    return score, blur_map


if __name__ == '__main__':
    dataset_path = "/home/CAMPUS/daiz1/Documents/endoscopic/Dataset"
    vid_idx = "0B591A3B-D063-4448-8932-734A65BCF960-9374-00000A2E90477438"
    workspace_path = "/home/CAMPUS/daiz1/Pictures"
    
    #filename = "Scope\ 1\ 2018-11-12\ 09.31.16.mov"
    filename = "Scope\ 1\ 2018-11-12\ 09.31.16\(2\).mov"

    vid_path = join(dataset_path, vid_idx, filename)
    workdir_path = join(workspace_path, vid_idx)

    if not os.path.exists(join("/home/CAMPUS/daiz1/Pictures", vid_idx)):
        os.makedirs(join("/home/CAMPUS/daiz1/Pictures", vid_idx))

    #os.system("ffmpeg -i {0} -f image2 -vf fps=fps=1 /home/CAMPUS/daiz1/Pictures-output%d.png".format(vid_path))
    
    #print("Number of 'I'ntra frames:")
    #os.system("ffmpeg -i {0} -vf \"showinfo\" -f null -".format(vid_path, vid_idx))
    
    os.system("ffmpeg -i {0} -vf \"select='eq(pict_type,I)'\" -vsync vfr {1}/out-%02d.jpeg".format(vid_path, workdir_path))
    
    scores = {}
    
    for item in os.listdir(workdir_path):
        if item.endswith('.jpeg'):
            scr, blur_img = detect_blur(join(workdir_path, item))
            
            scores[item] = scr
            
    print(scores)
    print("\nMost clear image: ", min(scores, key=scores.get))
    
