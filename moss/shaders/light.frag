#version 460

in DATA {
    vec3 position;
    vec2 texCoord;
    vec3 normal;
    vec3 cameraPosition;
    mat4 proj;
    mat4 view;
    mat4 model;
} data_in;

uniform vec4 color;

void main() {
    gl_FragColor = color;
}