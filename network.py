import _init_paths
import os
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, sys, cv2
import argparse
import glob
import json



#The main class containing network object and two detection methods
class Network():
    
    CLASSES = ('__background__',\
                        'aeroplane', 'bicycle', 'bird', 'boat',\
                        'bottle', 'bus', 'car', 'cat', 'chair',\
                        'cow', 'diningtable', 'dog', 'horse',\
                        'motorbike', 'person', 'pottedplant',\
                        'sheep', 'sofa', 'train', 'tvmonitor')
    
    network_map={"lite":["pvanet/models/pvanet/lite/test.pt", "pvanet/models/pvanet/lite/test.model"],\
            "full":["pvanet/models/pvanet/full/test.pt","pvanet/models/pvanet/full/test.model"]}
    
    
    
    def __init__(self, option="full", gpu_id=0):      
                
        prototxt, caffemodel = self.network_map[option]
        if not os.path.isfile(caffemodel):
            raise IOError(('{:s} not found.\nDid you run ./data/script/'
                           'fetch_faster_rcnn_models.sh?').format(caffemodel))  
        
        caffe.set_mode_gpu()
        cfg.GPU_ID = gpu_id
        cfg_from_file("pvanet/models/pvanet/cfgs/submit_160715.yml")
        print("Loading Network to GPU")
        self._net = caffe.Net(prototxt, caffemodel, caffe.TEST)

   
    
    #Detection function for single image
    def detect(self, img_path, CONF_THRESH=0.5):
        result = []
        _t = {'im_preproc': Timer(), 'im_net' : Timer(), 'im_postproc': Timer(), 'misc' : Timer()}
        im = cv2.imread(img_path)
        if im is None:
            print("Image: {} does not exist or the file is broken".format(img_path))
            return results
        else:
            print("Detecting image: {}".format(img_path))
            
            
        timer = Timer()
        timer.tic()
        scores, boxes = im_detect(self._net, im, _t)
        timer.toc()
        #print ('Detection took {:.3f}s for '
               #'{:d} object proposals').format(timer.total_time, boxes.shape[0])


        

        NMS_THRESH = 0.3
        for cls_ind, cls in enumerate(self.CLASSES[1:]):
            cls_ind += 1 # because we skipped background
            cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes,
                              cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, NMS_THRESH)
            dets = dets[keep, :]
            thresh = 0
            inds = np.where(dets[:, -1] > CONF_THRESH)[0] 
            
            for i in inds:
                bbox = dets[i, :4]
                score = float(dets[i, -1])
           
                xmin, ymin, xmax, ymax = bbox
                xmin, ymin, xmax, ymax = float(xmin), float(ymin), float(xmax), float(ymax)
                detection= {"class":cls,"xmin":xmin,"ymin":ymin,"xmax":xmax,\
                    "ymax":ymax, "score":score}
                result.append(detection)
                
        return sorted(result, key=lambda x: x["score"], reverse=True)      
     
   
    
    
    #Detection Function for a folder containing images
    def detect_folder(self, img_dir, img_format="jpg", CONF_THRESH=0.5):
        
        results = {"input_dir": img_dir}
        if not os.path.isdir(img_dir):
            print("The image directory: {} does not exist".format(img_dir))
            return results


        img_list = glob.glob(os.path.join(img_dir, "*.{}".format(img_format)))
        for img_path in img_list:
            results[os.path.basename(img_path)] = self.detect(img_path,CONF_THRESH)

       
        return results


    
#Unitest Function
def test():
           
    net = Network()
    print("Testting detect function") 
    im_names = im_names = ['000456.jpg', '000542.jpg', '001150.jpg', '001763.jpg', '004545.jpg']
    for im_name in im_names:
        img_path = os.path.join(os.getcwd(),"pvanet", "data/demo", im_name)
        print(net.detect(img_path))

    print("Testing detect_folder")
    input_folder = "pvanet/data/demo"
    print(net.detect_folder(input_folder))
    
    print("Testing OK!")
    

if __name__ == "__main__":
    test()