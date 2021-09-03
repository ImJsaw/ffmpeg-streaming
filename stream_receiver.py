"""receive frames from the sender"""
import subprocess as sp
import numpy as np
import cv2


class FFmpegReceiver:
    def __init__(self, stream_ip,w=1080, h=1920):
        self.ip = stream_ip        
        self.frame_size_w = w
        self.frame_size_h = h
        self.size_str = '%dx%d' % (w, h)
        self.rtspUrl = 'rtsp://%s:%d/test' % (self.ip, 8554)
        self.command = [
            'ffmpeg',
			#----   get from net --- #
            '-f', 'rtsp',  # 强制输入或输出文件格式
            '-rtsp_transport', 'tcp',  # 强制使用 tcp 通信
            '-timeout', '10',  # tcp timeout setting, must use in receiver
            '-i', self.rtspUrl,  # 输入
			# --- send to pipe --- #
            '-f', 'image2pipe',  # 强制输出到管道
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-video_size', self.size_str,  # 设置图像尺寸
            
			#ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
			'-preset', 'ultrafast',
            '-']
        self.pipe = sp.Popen(self.command, stdout=sp.PIPE)

    def read(self):
        frame = self.pipe.stdout.read(self.frame_size_w*self.frame_size_h*3)
        if frame is not None:
            frame = np.frombuffer(frame, dtype='uint8')
            return frame.reshape((self.frame_size_w, self.frame_size_h, 3))
        else:
            return None

    def receive(self):
        count = 0
        while True:
            frame = self.read()
            if frame is not None:
                print("No. %d: " % count, np.mean(frame))
                count += 1
                cv2.imshow("frame", frame)
                #cv2.imwrite('temp/%d.jpeg' % count, frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            self.pipe.stdout.flush()


if __name__ == '__main__':
    streamer = FFmpegReceiver('127.0.0.1')
    streamer.receive()
