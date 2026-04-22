
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import numpy as np

class PhotoReceiver(Node):
    def __init__(self):
        super().__init__('photo_receiver')
        self.subscription = self.create_subscription(
            Image,
            '/photo/image',
            self.callback,
            10
        )
        self.bridge = CvBridge()
        self.save_dir = os.path.expanduser("~/received_photos")
        os.makedirs(self.save_dir, exist_ok=True)

        self.count = 0
        self.get_logger().info("Photo receiver started")
        self.prev = None;

    def callback(self, msg):
        print("\nmsg: ", msg)
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        print("\nimg: ", img)
        filename = f"{self.save_dir}/photo_{self.count}.jpg"
        curr = img
        print("\nCurr_hash: ",curr)
        print("\nPrev_hash: ",self.prev)
        if self.prev is not None and np.array_equal(self.prev, curr):
            return
        self.prev = curr
        cv2.imwrite(filename, img)

        self.get_logger().info(f"Saved {filename}")
        self.count += 1

def main():
    rclpy.init()
    node = PhotoReceiver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
