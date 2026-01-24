import depthai as dai
import numpy as np
def save_ply(points, filename):
    # Filter out invalid points (0,0,0)
    non_zero = np.any(points != 0, axis=1)
    points = points[non_zero]

    # PLY Header
    header = f"""ply
format ascii 1.0
element vertex {len(points)}
property float x
property float y
property float z
end_header
"""
    with open(filename, 'w') as f:
        f.write(header)
        # Save points with 4 decimal places for efficiency
        np.savetxt(f, points, fmt='%f %f %f')
# 1. Setup (v3 style)
p = dai.Pipeline()
# 1. Create the source (StereoDepth requires Mono cameras)
monoL = p.create(dai.node.MonoCamera)
monoR = p.create(dai.node.MonoCamera)
stereo = p.create(dai.node.StereoDepth)

# 2. Configure sources
monoL.setBoardSocket(dai.CameraBoardSocket.CAM_B)
monoR.setBoardSocket(dai.CameraBoardSocket.CAM_C)

# 3. Link Cameras to Stereo
monoL.out.link(stereo.left)
monoR.out.link(stereo.right)
cloud = p.create(dai.node.PointCloud)
stereo.depth.link(cloud.inputDepth) # This is why it was stalling!
# Configure StereoDepth
# stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY) # Good starting point
stereo.setSubpixel(True)
stereo.setLeftRightCheck(True)
stereo.setSubpixelFractionalBits(3)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)

# Set a confidence threshold: lower means more strict (0-255)
# 200 is usually a safe bet to filter out random meaningless dots
# Enable a suite of filters to clean up the "meaningless" noise
post_process = stereo.initialConfig.getPostProcessing()
post_process.speckleFilter.enable = True
post_process.speckleFilter.speckleRange = 50
post_process.spatialFilter.enable = True
post_process.spatialFilter.holeFillingRadius = 2
post_process.temporalFilter.enable = True

# Update the node with these settings
stereo.initialConfig.setPostProcessing(post_process)
stereo.initialConfig.setConfidenceThreshold(150)

# Link to PointCloud
# 2. No XLinkOut needed! Just create an output queue directly from the node
# This automatically handles the "XLink" bridge for you
out_q = cloud.outputPointCloud.createOutputQueue()

# 3. Start and Save
p.start() 
while p.isRunning():
    # Retrieve the message
    pcl_msg = out_q.get() 
    print('made it')
    points = pcl_msg.getPoints() # Get the (x,y,z) array
    
    if len(points.shape) != 2:
        points = points.reshape(-1, 3)
    # Save it
    np.save("cloud_v3.npy", points)
    print("Point cloud saved.")
    break