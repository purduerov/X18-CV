import depthai as dai
import numpy as np

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