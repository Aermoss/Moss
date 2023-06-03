import moss, glm

def intersectAABB(a, b):
    a = a.transform
    b = b.transform

    return (
        a.position.x - a.scaleVector.x <= b.position.x + b.scaleVector.x and \
        a.position.x + a.scaleVector.x >= b.position.x - b.scaleVector.x and \
        a.position.y - a.scaleVector.y <= b.position.y + b.scaleVector.y and \
        a.position.y + a.scaleVector.y >= b.position.y - b.scaleVector.y and \
        a.position.z - a.scaleVector.z <= b.position.z + b.scaleVector.z and \
        a.position.z + a.scaleVector.z >= b.position.z - b.scaleVector.z
    )

def isPointInsideAABB(point, box):
    box = box.transform

    return (
        point.x <= box.position.x + box.scaleVector.x and \
        point.x >= box.position.x - box.scaleVector.x and \
        point.y <= box.position.y + box.scaleVector.y and \
        point.y >= box.position.y - box.scaleVector.y and \
        point.z <= box.position.z + box.scaleVector.z and \
        point.z >= box.position.z - box.scaleVector.z
    )