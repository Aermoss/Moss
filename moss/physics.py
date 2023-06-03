import moss, math, glm

epsilon = 0.00000001
gravity = 9.80665

xAxis = glm.vec3(1.0, 0.0, 0.0)
yAxis = glm.vec3(0.0, 1.0, 0.0)
zAxis = glm.vec3(0.0, 0.0, 1.0)

forward = xAxis
up = yAxis
right = zAxis
backward = -xAxis
down = -yAxis
left = -zAxis

def sq(a):
    return a * a

def scale(input, inMin, inMax, outMin, outMax):
    input = glm.clamp(input, inMin, inMax)
    return (input - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

def lerp(a, b, t):
    t = glm.clamp(t, 0.0, 1.0)
    return a + t * (b - a)

def inverseLerp(a, b, v):
    v = glm.clamp(v, a, b)
    return (v - a) / (b - a)

def moveTowards(current, target, speed):
    if abs(target - current) <= speed:
        return target
    
    return current + glm.sign(target - current) * speed

class Element:
    def __init__(self, size, position, inertia, offset, mass):
        self.size = size
        self.position = position
        self.inertia = inertia
        self.offset = offset
        self.mass = mass

    def volume(self):
        return self.size.x * self.size.y * self.size.z
    
def sphere(radius, mass):
    return glm.vec3((2.0 / 5.0) * mass * sq(radius))

def cube(size, mass):
    return glm.vec3((1.0 / 6.0) * mass * sq(size))

def cuboid(size, mass):
    C = (1.0 / 12.0) * mass
    return glm.vec3(sq(size.y) + sq(size.z), sq(size.x) + sq(size.z), sq(size.x) + sq(size.y)) * C

def cylinder(radius, length, mass):
    C = (1.0 / 12.0) * mass
    I = glm.vec3(0.0)
    I.x = (0.5) * mass * sq(radius)
    I.y = I.z = C * (3.0 * sq(radius) + sq(length))
    return I

def cubeElement(position, size, mass):
    return Element(size, position, cuboid(size, mass), position, mass)

def computeUniformMass(elements, totalMass):
    totalVolume = 0.0

    for element in elements:
        totalVolume += element.volume()

    for element in elements:
        element.mass = (element.volume() / totalVolume) * totalMass

def tensor(momentOfIntertia):
    return glm.mat3(
        momentOfIntertia.x, 0.0, 0.0, 
        0.0, momentOfIntertia.y, 0.0, 
        0.0, 0.0, momentOfIntertia.z
    )

def tensorElement(elements, precomputedOffset = False, cg = None):
    Ixx, Iyy, Izz = 0.0, 0.0, 0.0
    Ixy, Ixz, Iyz = 0.0, 0.0, 0.0

    mass = 0.0
    moment = glm.vec3(0.0)

    for element in elements:
        mass += element.mass
        moment += element.mass * element.position

    centerOfGravity = moment / mass

    for element in elements:
        if not precomputedOffset:
            element.offset = element.position - centerOfGravity

        else:
            element.offset = element.position

        offset = element.offset

        Ixx += element.inertia.x + element.mass * (sq(offset.y) + sq(offset.z))
        Iyy += element.inertia.y + element.mass * (sq(offset.z) + sq(offset.x))
        Izz += element.inertia.z + element.mass * (sq(offset.x) + sq(offset.y))
        Ixy += element.mass * (offset.x * offset.y)
        Ixz += element.mass * (offset.x * offset.z)
        Iyz += element.mass * (offset.y * offset.z)

    if cg != None:
        cg.x, cg.y, cg.z = \
            centerOfGravity.x, centerOfGravity.y, centerOfGravity.z
        
    return glm.mat3(
        Ixx, -Ixy, -Ixz, 
       -Ixy,  Iyy, -Iyz, 
       -Ixz, -Iyz,  Izz
    )

def knots(metersPerSecond):
    return metersPerSecond * 1.94384

def metersPerSecond(kilometersPerHour):
    return kilometersPerHour / 3.6

def kilometersPerHour(metersPerSecond):
    return metersPerSecond * 3.6

def kelvin(celsius):
    return celsius - 273.15

def watts(horsepower):
    return horsepower * 745.7

class CollisionInfo:
    def __init__(self, point, normal, penetration):
        self.point = point
        self.normal = normal
        self.penetration = penetration

class RigidBody:
    def __init__(self, mass, inertia):
        self.position = glm.vec3(0.0)
        self.velocity = glm.vec3(0.0)
        self.angularVelocity = glm.vec3(0.0)
        self.mass = mass
        self.inertia = inertia
        self.inverseInertia = glm.inverse(inertia)
        self.orientation = glm.quat(1.0, 0.0, 0.0, 0.0)
        self.force = glm.vec3(0.0)
        self.torque = glm.vec3(0.0)
        self.applyGravity = True
        self.active = True

    def getPointAngularVelocity(self, point):
        return glm.cross(self.angularVelocity, point)
    
    def getPointVelocity(self, point):
        return self.inverseTransformDirection(self.velocity) + self.getPointAngularVelocity(point)
    
    def getBodyVelocity(self):
        return self.inverseTransformDirection(self.velocity)
    
    def getInverseMass(self):
        return 1.0 / self.mass
    
    def addForceAtPoint(self, force, point):
        self.force += self.transformDirection(force)
        self.torque += glm.cross(point, force)

    def transformDirection(self, direction):
        return self.orientation * direction
    
    def inverseTransformDirection(self, direction):
        return glm.inverse(self.orientation) * direction
    
    def setInertiaTensor(self, tensor):
        self.inertia = tensor
        self.inverseInertia = glm.inverse(tensor)

    def setInertiaMoment(self, moment):
        self.setInertiaTensor(tensor(moment))

    def addLinearImpulse(self, impulse):
        self.velocity += impulse / self.mass

    def addRelativeLinearImpulse(self, impulse):
        self.velocity += self.transformDirection(impulse) / self.mass

    def addAngularImpulse(self, impulse):
        self.angularVelocity += self.inverseTransformDirection(impulse) * self.inverseInertia

    def addRelativeAngularImpulse(self, impulse):
        self.angularVelocity += impulse * self.inverseInertia

    def addForce(self, force):
        self.force += force

    def addRelativeForce(self, force):
        self.force += self.transformDirection(force)

    def addTorque(self, torque):
        self.torque += self.inverseTransformDirection(torque)

    def addRelativeTorque(self, torque):
        self.torque += torque

    def addFriction(self, normal, slidingDirection, frictionCoeff):
        weight = self.mass * gravity
        normalForce = weight * max(glm.dot(normal, up), 0.0)
        return -slidingDirection * normalForce * frictionCoeff
    
    def getSpeed(self):
        return glm.length(self.velocity)
    
    def getEulerAngles(self):
        return glm.eulerAngles(self.orientation)
    
    def getTorque(self):
        return self.torque
    
    def getForce(self):
        return self.force
    
    def forward(self):
        return self.transformDirection(forward)
    
    def up(self):
        return self.transformDirection(up)
    
    def right(self):
        return self.transformDirection(right)

    def update(self, dt):
        if not self.active: return

        acceleration = self.force / self.mass

        if self.applyGravity: acceleration.y -= gravity

        self.velocity += acceleration * dt
        self.position += self.velocity * dt

        self.angularVelocity += self.inverseInertia * (self.torque - glm.cross(self.angularVelocity, self.inertia * self.angularVelocity)) * dt
        self.orientation += (self.orientation * glm.quat(0.0, self.angularVelocity)) * (0.5 * dt)
        self.orientation = glm.normalize(self.orientation)
        self.force, self.torque = glm.vec3(0.0), glm.vec3(0.0)

def linearImpulseCollisionResponse(a, b, collisionInfo, restitutionCoeff = 0.66):
    totalInverseMass = a.getInverseMass() + b.getInverseMass()

    a.position -= collisionInfo.normal * collisionInfo.penetration * (a.getInverseMass() / totalInverseMass)
    b.position += collisionInfo.normal * collisionInfo.penetration * (b.getInverseMass() / totalInverseMass)

    relativeVelocity = b.velocity - a.velocity

    impulseForce = glm.dot(relativeVelocity, collisionInfo.normal)

    j = (-(1 + restitutionCoeff) * impulseForce) / totalInverseMass
    impulse = j * collisionInfo.normal

    a.addLinearImpulse(-impulse)
    b.addLinearImpulse(+impulse)

def linearImpulseCollisionResponse(a, b, collisionInfo, restitutionCoeff = 0.66):
    totalInverseMass = a.getInverseMass() + b.getInverseMass()

    a.position -= collisionInfo.normal * collisionInfo.penetration * (a.getInverseMass() / totalInverseMass)
    b.position += collisionInfo.normal * collisionInfo.penetration * (b.getInverseMass() / totalInverseMass)

    aRelative = collisionInfo.point - a.position
    bRelative = collisionInfo.point - b.position

    aVelocity = a.getPointVelocity(aRelative)
    bVelocity = b.getPointVelocity(bRelative)

    relativeVelocity = b.transformDirection(bVelocity) - a.transformDirection(aVelocity)

    impulseForce = glm.dot(relativeVelocity, collisionInfo.normal)

    aInertia = glm.cross(a.inertia * glm.cross(aRelative, collisionInfo.normal), aRelative)
    bInertia = glm.cross(b.inertia * glm.cross(bRelative, collisionInfo.normal), bRelative)
    
    angularEffectOne = glm.dot(aInertia + bInertia, collisionInfo.normal)
    angularEffectTwo = \
        glm.dot(collisionInfo.normal, glm.cross((glm.cross(aRelative, collisionInfo.normal) / a.inertia), aRelative)) + \
        glm.dot(collisionInfo.normal, glm.cross((glm.cross(bRelative, collisionInfo.normal) / b.inertia), bRelative))

    if abs(angularEffectOne - angularEffectTwo) < epsilon:
        return

    j = (-(1 + restitutionCoeff) * impulseForce) / (totalInverseMass + angularEffectOne)
    impulse = j * collisionInfo.normal

    a.addLinearImpulse(-impulse)
    b.addLinearImpulse( impulse)

    a.addAngularImpulse(glm.cross(aRelative, -impulse))
    b.addAngularImpulse(glm.cross(bRelative,  impulse))

class ForceGenerator():
    def applyForces(rigidBody, dt): ...