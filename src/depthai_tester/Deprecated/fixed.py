import depthai as dai
import numpy as np

def save_ply(points, filename):
    # Filter out (0,0,0) points which represent 'no depth'
    non_zero = np.any(points != 0, axis=1)
    valid_points = points[non_zero]
    
    header = f"ply\nformat ascii 1.0\nelement vertex {len(valid_points)}\nproperty float x\nproperty float y\nproperty float z\nend_header\n"
    with open(filename, 'w') as f:
        f.write(header)
        np.savetxt(f, valid_points, fmt='%f %f %f')

p = dai.Pipeline()

# Nodes
monoL = p.create(dai.node.MonoCamera)
monoR = p.create(dai.node.MonoCamera)
stereo = p.create(dai.node.StereoDepth)
cloud = p.create(dai.node.PointCloud)

# Config
monoL.setBoardSocket(dai.CameraBoardSocket.CAM_B)
monoR.setBoardSocket(dai.CameraBoardSocket.CAM_C)

# Critical Fixes for "Lines" and "Empty Frames"
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.FAST_DENSITY)
stereo.setSubpixel(True)
stereo.setLeftRightCheck(True)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.initialConfig.setConfidenceThreshold(150)
# Linking
monoL.out.link(stereo.left)
monoR.out.link(stereo.right)
stereo.depth.link(cloud.inputDepth)

# Output
out_q = cloud.outputPointCloud.createOutputQueue()

p.start()
print("Point the camera at a textured object (not a blank wall)...")

while p.isRunning():
    pcl_msg = out_q.get()
    points = pcl_msg.getPoints()
    
    if len(points) > 0:
        save_ply(points.reshape(-1, 3), "output_cloud.ply")
        print(f"Saved {len(points)} points to output_cloud.ply")
        break