import cadquery as cq

BOXES = (
    #depth (x), length(y), height(z)
    # We should only need to change length and height
    (5,8,3),
    (5,3,8),
    (5,8,5),
)


# Create a simple cube
def create_box(depth, length, height):
    return cq.Workplane("XY").box(depth, length, height)

def center_assembly(assembly, length):
    center_assembly = cq.Assembly()
    center_assembly.add(assembly, name="assembly", loc=cq.Location((0,-length/2,0)))
    return center_assembly


def create_multibox(boxes):
    cubes = [create_box(*dim) for dim in boxes]
    assembly = cq.Assembly()
    cur_y = 0
    for i in range(len(boxes)):
        cube = cubes[i]
        dim = boxes[i]
        cur_y += dim[1]/2
        assembly.add(cube, name="cube"+str(i), loc=cq.Location((0,cur_y ,dim[2]/2)))
        cur_y += dim[1]/2
    return assembly


if __name__ == "__main__":
    combined_cubes = create_multibox(BOXES)
    combined_shape = combined_cubes
    centered = center_assembly(combined_shape, sum([dim[1] for dim in BOXES]))

    shape_compound = centered.toCompound()
    # Save the cube as an STL file
    file_path = "object.stl"
    cq.exporters.export(shape_compound, file_path)

    print(f"object saved as {file_path}")