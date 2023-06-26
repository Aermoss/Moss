import flight_model, math, glm
import moss.physics as phi

def getInterceptPoint(position, velocity, targetPosition, targetVelocity):
    velocityDelta = targetVelocity - velocity
    positionDelta = targetPosition - position
    timeToIntercept = glm.length(positionDelta) / glm.length(velocityDelta)
    print(timeToIntercept)
    return targetPosition + targetVelocity * timeToIntercept

def follow(airplane: flight_model.Airplane, target: glm.vec3):
    direction = glm.normalize(airplane.inverseTransformDirection(target - airplane.position))
    # angle = glm.angle(phi.forward, direction)
    angle = glm.acos(glm.dot(glm.normalize(phi.forward), glm.normalize(direction)))
    rudder = direction.z
    elevator = direction.y * 5.0
    m = math.pi / 4.0
    agressiveRoll = direction.z
    wingsLevelRoll = airplane.right().y
    wingsLevelInfluence = phi.inverseLerp(0.0, m, glm.clamp(angle, -m, m))
    aileron = phi.lerp(wingsLevelRoll, agressiveRoll, wingsLevelInfluence)
    airplane.control = glm.clamp(glm.vec4(aileron, rudder, elevator, 0.0), glm.vec4(-1.0), glm.vec4(1.0))