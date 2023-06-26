// Moss Editor

include "rsxio", "rsxmath", "moss_api.rsxh" : *;

namespace object {
    int id;
    float[3] position;
    float[3] rotation;
    float[3] scale;
};

namespace window {
    int id;
    int[] size;
};

namespace camera {
    float yaw;
    float pitch;
    float speed;
    float[3] position;
};

float lerp(float a, float b, float f) {
    return a + f * (b - a);
}

float[] normalize(float[] v) {
    float length_of_v = std::sqrt((v[0] * v[0]) + (v[1] * v[1]) + (v[2] * v[2]));
    return {std::divf(v[0], length_of_v), std::divf(v[1], length_of_v), std::divf(v[2], length_of_v)};
}

float negate(float value) {
    return -value;
}

float[] cross(float[] a, float[] b) {
    return {a[1] * b[2] - a[2] * b[1], negate(a[0] * b[2] - a[2] * b[0]), a[0] * b[1] - a[1] * b[0]};
}

void setup() {
    object::id = moss::getObjectID();
    window::id = moss::getWindowID();

    object::position = moss::transform::getPosition(object::id);
    object::rotation = moss::transform::getRotation(object::id);
    object::scale = moss::transform::getScale(object::id);
    
    float[] rotation = moss::camera::getRotation();
    camera::pitch = rotation[0];
    camera::yaw = rotation[1];
    camera::position = moss::camera::getPosition();

    std::rout("Hello from R# with ID: " + (string) object::id + std::endl());
    window::size = moss::window::getSize(window::id);
    moss::input::setCursorPosition({window::size[0] / 2, window::size[1] / 2});
    return;
}

int vr() {
    camera::speed = 0.1f;
    float[] d = moss::vr::getHmdDirection();
    float yaw = -std::atan2(d[0], d[2]) - std::radians(90.0f);
    float[] front = {std::cos(yaw), 0.0f, std::sin(yaw)};
    float[] up = {0.0f, 1.0f, 0.0f};
    float[] joystickPosition = moss::vr::getControllerJoystickPosition(moss::vr::controllerRight);

    if (joystickPosition[1] != 0.0f) {
        camera::position[0] += front[0] * camera::speed * joystickPosition[1];
        camera::position[2] += front[2] * camera::speed * joystickPosition[1];
    }

    if (joystickPosition[0] != 0.0f) {
        float[] vector = normalize(cross(front, up));
        camera::position[0] += vector[0] * camera::speed * joystickPosition[0];
        camera::position[2] += vector[2] * camera::speed * joystickPosition[0];
    }
    
    moss::camera::setPosition(camera::position);
    return 0;
}

int nonvr() {
    if (moss::input::getKey(MOSS_KEY_LEFT_CONTROL)) camera::speed = 0.1f;
    else camera::speed = 0.05f;

    if (moss::input::getKey(MOSS_KEY_SPACE))
        camera::position[1] += 1.0f * camera::speed;

    if (moss::input::getKey(MOSS_KEY_LEFT_SHIFT))
        camera::position[1] -= 1.0f * camera::speed;

    moss::input::setCursorVisible(false);

    if (moss::input::getKey(MOSS_KEY_W)) {
        camera::position[0] += std::cos(std::radians(camera::yaw)) * camera::speed;
        camera::position[2] += std::sin(std::radians(camera::yaw)) * camera::speed;
    }

    if (moss::input::getKey(MOSS_KEY_S)) {
        camera::position[0] -= std::cos(std::radians(camera::yaw)) * camera::speed;
        camera::position[2] -= std::sin(std::radians(camera::yaw)) * camera::speed;
    }

    if (moss::input::getKey(MOSS_KEY_A)) {
        float[] vector = normalize(cross({std::cos(std::radians(camera::yaw)), 0.0f, std::sin(std::radians(camera::yaw))}, {0.0f, 1.0f, 0.0f}));
        camera::position[0] -= vector[0] * camera::speed;
        camera::position[2] -= vector[2] * camera::speed;
    }

    if (moss::input::getKey(MOSS_KEY_D)) {
        float[] vector = normalize(cross({std::cos(std::radians(camera::yaw)), 0.0f, std::sin(std::radians(camera::yaw))}, {0.0f, 1.0f, 0.0f}));
        camera::position[0] += vector[0] * camera::speed;
        camera::position[2] += vector[2] * camera::speed;
    }

    float[] cursor_pos = moss::input::getCursorPosition();

    float x_offset = std::divf(100 * (cursor_pos[0] - (int) (window::size[0] / 2)), window::size[0]);
    float y_offset = std::divf(100 * (cursor_pos[1] - (int) (window::size[1] / 2)), window::size[1]);

    camera::yaw += x_offset;
    camera::pitch -= y_offset;

    if (camera::pitch >= 89.9f) camera::pitch = 89.9f;
    if (camera::pitch <= -89.9f) camera::pitch = -89.9f;

    moss::camera::setPosition(camera::position);
    moss::input::setCursorPosition({window::size[0] / 2, window::size[1] / 2});
    moss::camera::setRotation({camera::pitch, camera::yaw});
    return 0;
}

void update() {
    if (moss::window::getSize(window::id) != window::size) {
        window::size = moss::window::getSize(window::id);
        std::rout("window resized: " + (string) window::size[0] + ", " + (string) window::size[1] + std::endl());
    }
    
    if (moss::camera::isVR()) vr();
    else nonvr();

    moss::transform::setPosition(object::id, object::position);
    moss::transform::setRotation(object::id, object::rotation);
    moss::transform::setScale(object::id, object::scale);
    return;
}