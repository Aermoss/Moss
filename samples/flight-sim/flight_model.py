import math, sys, glm, data
import moss.physics as phi

from typing import overload, List

def getAirTemperature(altitude):
    return 288.15 - 0.0065 * altitude

def getAirPressure(altitude):
    return 101325.0 * pow(1 - 0.0065 * (altitude / 288.15), 5.25)

def getAirDensity(altitude):
    return 0.00348 * (getAirPressure(altitude) / getAirTemperature(altitude))

class Airfoil:
    def __init__(self, curve):
        self.minAlpha, self.maxAlpha = curve[0].x, curve[len(curve) - 1].x
        self.data = curve

    def sample(self, alpha):
        maxIndex = len(self.data) - 1
        t = phi.inverseLerp(self.minAlpha, self.maxAlpha, alpha) * maxIndex
        if math.isnan(t): return (0.0, 0.0)
        integer = math.floor(t)
        fractional = t - integer
        index = int(integer)
        value = phi.lerp(self.data[index], self.data[index + 1], fractional) if index < maxIndex else self.data[maxIndex]
        return (value.y, value.z)

class Engine:
    throttle = 0.25
    def applyForces(self, rigidBody, deltaTime): ...

class SimpleEngine(Engine):
    def __init__(self, thrust):
        self.thrust = thrust

    def applyForces(self, rigidBody, deltaTime):
        rigidBody.addRelativeForce(glm.vec3(self.throttle * self.thrust, 0.0, 0.0))

class PropellorEngine(Engine):
    def __init__(self, horsePower, rpm, diameter):
        self.horsePower = horsePower
        self.rpm = rpm
        self.diameter = diameter

    def applyForces(self, rigidBody: phi.RigidBody, deltaTime: float):
        speed = rigidBody.getSpeed()
        altitude = rigidBody.position.y
        enginePower = phi.watts(self.horsePower)
        a, b, c = 1.83, -1.32, 0.12
        turnoverRate = self.rpm / 60.0
        propellorAdvaceRatio = speed / (turnoverRate * self.diameter)
        propellorEfficiency = a * propellorAdvaceRatio + b * pow(propellorAdvaceRatio, 3)
        powerDropOffFactor = ((getAirDensity(altitude) / getAirDensity(0.0)) - c) / (1 - c)
        thrust = ((propellorEfficiency * enginePower) / speed) * powerDropOffFactor
        rigidBody.addRelativeForce(glm.vec3(self.throttle * thrust, 0.0, 0.0))

class Wing(phi.ForceGenerator):
    def __init__(self, position: glm.vec3, span: float, airfoil: Airfoil, area = None, chord = None, normal: glm.vec3 = phi.up):
        self.liftMultiplier = 1.0
        self.dragMultiplier = 1.0
        self.efficiencyFactor = 1.0
        self.deflection = 0.0
        self.controlInput = 0.0
        self.minDeflection = -10.0
        self.maxDeflection = 10.0
        self.maxActuatorSpeed = 90.0
        self.maxActuatorTorque = 6000.0
        self.incidence = 0.0
        self.isControlSurface = True
        self.airfoil = airfoil
        self.centerOfPressure = position
        self.chord = chord
        self.area = area
        self.span = span

        if self.chord is None:
            self.chord = (self.area / self.span)

        if self.area is None:
            self.area = (self.span * self.chord)

        self.normal = normal
        self.aspectRatio = pow(self.span, 2) / self.area

    def setControlInput(self, input: float):
        self.controlInput = glm.clamp(input, -1.0, 1.0)
    
    def setDeflectionLimits(self, min: float, max: float):
        self.minDeflection = min
        self.maxDeflection = max

    def applyForces(self, rigidBody: phi.RigidBody, deltaTime: float):
        localVelocity = rigidBody.getPointVelocity(self.centerOfPressure)
        speed = glm.length(localVelocity)
        if speed <= phi.epsilon: return
        wingNormal = self.deflectWing(rigidBody, deltaTime) if self.isControlSurface else self.normal
        dragDirection = glm.normalize(-localVelocity)
        liftDirection = glm.normalize(glm.cross(glm.cross(dragDirection, wingNormal), dragDirection))
        angleOfAttack = glm.degrees(math.asin(glm.dot(dragDirection, wingNormal)))
        liftCoeff, dragCoeff = self.airfoil.sample(angleOfAttack)
        inducedDragCoeff = pow(liftCoeff, 2) / (math.pi * self.aspectRatio * self.efficiencyFactor)
        dynamicPressure = 0.5 * pow(speed, 2) * getAirDensity(0.0) * self.area
        lift = liftDirection * liftCoeff * self.liftMultiplier * dynamicPressure
        drag = dragDirection * (dragCoeff + inducedDragCoeff) * self.dragMultiplier * dynamicPressure
        rigidBody.addForceAtPoint(lift + drag, self.centerOfPressure)

    def deflectWing(self, rigidBody: phi.RigidBody, deltaTime: float):
        self.deflection = (self.maxDeflection if self.controlInput >= 0.0 else self.minDeflection) * abs(self.controlInput)
        axis = glm.normalize(glm.cross(phi.forward, self.normal))
        rotation = glm.rotate(glm.mat4(1.0), glm.radians(self.incidence + self.deflection), axis)
        return glm.vec3(rotation * glm.vec4(self.normal, 1.0))

class Airplane(phi.RigidBody):
    def __init__(self, mass: float, inertia: glm.mat3, surfaces: List[Wing], engine: Engine):
        super().__init__(mass = mass, inertia = inertia)
        self.surfaces = surfaces
        self.engine = engine
        self.control = glm.vec4(0.0)
        self.isLanded = False

        self.surfaces[0].isControlSurface = False
        self.surfaces[3].isControlSurface = False
        self.surfaces[1].setDeflectionLimits(-15.0, 15.0)
        self.surfaces[2].setDeflectionLimits(-15.0, 15.0)
        self.surfaces[5].setDeflectionLimits(-5.0, 5.0)

    def update(self, deltaTime: float):
        aileron, rudder, elevator, trim = \
            self.control.x, self.control.y, self.control.z, self.control.w
        
        self.surfaces[1].setControlInput(aileron)
        self.surfaces[2].setControlInput(-aileron)
        self.surfaces[4].setControlInput(-elevator)
        self.surfaces[4].incidence = trim * 10.0
        self.surfaces[5].setControlInput(-rudder)

        for wing in self.surfaces:
            wing.applyForces(self, deltaTime)

        if self.isLanded:
            staticFrictionCoeff = 0.2
            kineticFrictionCoeff = 0.55

            if self.getSpeed() > phi.epsilon:
                self.addFriction(phi.up, glm.normalize(self.velocity), kineticFrictionCoeff)

        else:
            ...

        self.engine.applyForces(self, deltaTime)
        super().update(deltaTime)

    def getAltitude(self):
        return self.position.y
    
    def getG(self):
        velocity = self.getBodyVelocity()
        turnRadius = sys.float_info.max if (abs(self.angularVelocity.z) < phi.epsilon) else self.velocity.x / self.angularVelocity.z
        centrifugalAcceleration = phi.sq(velocity.x) / turnRadius
        gForce = centrifugalAcceleration / phi.gravity
        gForce += (self.up().y * phi.gravity) / phi.gravity
        return gForce
    
    def getMach(self):
        temperature = getAirTemperature(self.getAltitude())
        speedOfSound = math.sqrt(1.402 * 286.0 * temperature)
        return self.getSpeed() / speedOfSound
    
    def getAoA(self):
        velocity = self.getBodyVelocity()
        return glm.degrees(math.asin(glm.dot(glm.normalize(-velocity), phi.up)))
    
    def getIAS(self):
        airDensity = getAirDensity(self.getAltitude())
        dynamicPressure = 0.5 * pow(self.getSpeed(), 2) * airDensity
        return math.sqrt(2 * dynamicPressure / getAirDensity(0.0))