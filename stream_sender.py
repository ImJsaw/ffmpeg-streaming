"""H.264 Streaming methods"""
import numpy as np
import subprocess as sp
import time
import cv2
# from imageio import get_reader


class FrameGenerator:
    """
generate a frame of random gray scale
    """

    def __init__(self, size, source=None):
        self.size = size
        self.count = 0
        self.source = source
        if self.source is not None:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                print('Video not available.')
                time.sleep(50)
                self.source = None
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print("Image Size: %d x %d" % (width, height))
			#cap.set(cv2.CAP_PROP_FPS, 60.0) 
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
			
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            print("Image Size: %d x %d, %d" % (width, height, fps))
            time.sleep(2)
			
    def generate(self):
        """
    generate a frame
        :return:
        """
        frame_gray = np.random.randint(0, 255) * np.ones(self.size).astype('uint8')
        if self.source is None:
            time.sleep(50)
            return frame_gray
        else:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                self.cap = cv2.VideoCapture(self.source)
                return self.generate()


class FFmpegStreamer:
    def __init__(self, target_ip, target_port=8554, fps=25, w=1080, h=1920, rate=4096):
        self.frame_generator = FrameGenerator((256, 256, 3), source=0)
        self.target_ip = target_ip
        self.target_port = target_port
        self.fps = fps
        self.frame_size_w = w
        self.frame_size_h = h
        self.size_str = '%dx%d' % (self.frame_size_w, self.frame_size_h)
        self.rate = rate  # kbps
        self.rtspUrl = 'rtsp://%s:%d/test' % (self.target_ip, self.target_port)
        # written according to https://www.cnblogs.com/Manuel/p/15006727.html
        self.command = [
            'ffmpeg',
			#'-re',
			# ---------    format to h264 ----------#
            # '-y', # 无需询问即可覆盖输出文件
            '-f', 'rawvideo',  # 强制输入或输出文件格式
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-s', self.size_str,  # 设置图像大小
            '-r', str(fps),  # 设置帧率
            '-i', '-',  # 输入
            '-b:v', '%dk' % self.rate,  # 设置数据率
            '-c:v', 'libx264',
            '-x264opts', 'bitrate=%d' % self.rate,  # 设置比特率（kbps）
            '-pix_fmt', 'bgr24',
            
			#ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
            '-preset', 'ultrafast',
			#------   send to net ------------
            '-f', 'rtsp',  # 强制输入或输出文件格式
			
            # '-rtsp_transport', 'udp',  # 使用UDP推流
            '-rtsp_transport', 'tcp',  # 使用TCP推流
            self.rtspUrl]
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)
        self.count = 0

    def set_rate(self, rate):
        self.rate = rate
        self.command[10] = '%dk' % self.rate
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)

    def stream(self):
        frame = self.frame_generator.generate()
        cv2.imshow('cam',frame)
        self.pipe.stdin.write(frame.tostring())
        self.count += 1
        print('No. %d: ' % self.count, np.mean(frame))


if __name__ == '__main__':
    streamer = FFmpegStreamer('127.0.0.1', fps=25, rate=8192)
    while True:
        streamer.stream()

