# -*- coding: utf-8 -*-
import os
import sys
import time
import random
from PIL import Image
# from common import screenshot

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torch.autograd import Variable

SCALE = 1

class CNNEncoder(nn.Module):
    """docstring for ClassName"""
    def __init__(self):
        super(CNNEncoder, self).__init__()
        self.layer1 = nn.Sequential(
                        nn.Conv2d(3,64,kernel_size=3,padding=0),
                        nn.BatchNorm2d(64, momentum=1, affine=True),
                        nn.ReLU(),
                        nn.MaxPool2d(2))
        self.layer2 = nn.Sequential(
                        nn.Conv2d(64,64,kernel_size=3,padding=0),
                        nn.BatchNorm2d(64, momentum=1, affine=True),
                        nn.ReLU(),
                        nn.MaxPool2d(2))
        self.layer3 = nn.Sequential(
                        nn.Conv2d(64,64,kernel_size=3,padding=0),
                        nn.BatchNorm2d(64, momentum=1, affine=True),
                        nn.ReLU(),
                        nn.MaxPool2d(2))
        self.layer4 = nn.Sequential(
                        nn.Conv2d(64,64,kernel_size=3,padding=0),
                        nn.BatchNorm2d(64, momentum=1, affine=True),
                        nn.ReLU(),
                        nn.MaxPool2d(2))
        self.layer5 = nn.Sequential(
                        nn.Conv2d(64,64,kernel_size=3,padding=0),
                        nn.BatchNorm2d(64, momentum=1, affine=True),
                        nn.ReLU(),
                        nn.MaxPool2d(2))
        self.layer6 = nn.Linear(1600,1)

    def forward(self,x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.layer5(out)
        out = out.view(out.size(0),-1)
        out = self.layer6(out)

        return out # 64

def preprocess(img):
    w, h = img.size
    top =  (h - w)/2

    img = img.crop((0,top,w,w+top))
    img = img.convert('RGB')
    img = img.resize((224,224), resample=Image.LANCZOS)

    normalize = transforms.Normalize(mean=[0.92206, 0.92206, 0.92206], std=[0.08426, 0.08426, 0.08426])
    transform = transforms.Compose([transforms.ToTensor(),normalize])

    img = transform(img)

    return img

def set_button_position(img):
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = img.size
    # print(w,h)
    left = int(w / 2)
    top = int(1584 * (h / 1920.0))
    left = int(random.uniform(left-50, left+50))
    top = int(random.uniform(top-10, top+10))
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top

def jump(press_time):
    press_time = int(press_time*SCALE)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time
    )
    os.system(cmd)

def main():

    net = CNNEncoder()
    if os.path.exists("./model.pkl"):
        net.load_state_dict(torch.load("./model.pkl",map_location=lambda storage, loc: storage))
        print("load model")
    net.eval()

    print("load ok")

    i, next_rest, next_rest_time = (0, random.randrange(3, 10),
                                    random.randrange(5, 10))
    while True:
        # screenshot.pull_screenshot()
        os.system('adb exec-out screencap -p > autojump.png')
        img = Image.open('./autojump.png')
        set_button_position(img)
        img = preprocess(img)

        img = Variable(img.unsqueeze(0))
        press_time = net(img).data[0].numpy()
        # print(press_time)
        jump(press_time)

        i += 1
        if i == next_rest:
            print('alreay {} jumps, reset {}s'.format(i, next_rest_time))
            for j in range(next_rest_time):
                sys.stdout.write('\rafter {}s agine'.format(next_rest_time - j))
                sys.stdout.flush()
                time.sleep(1)
            print('\ngo')
            i, next_rest, next_rest_time = (0, random.randrange(30, 100),
                                            random.randrange(10, 20))
        # 为了保证截图的时候应落稳了，多延迟一会儿，随机值防 ban
        time.sleep(random.uniform(1.8, 2.4))

if __name__ == '__main__':
    main()