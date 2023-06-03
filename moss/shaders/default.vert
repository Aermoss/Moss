#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoord;
layout (location = 2) in vec3 normal;

out DATA {
    vec3 position;
    vec2 texCoord;
    vec3 normal;
    vec3 cameraPosition;
    mat4 proj;
    mat4 view;
    mat4 model;
} data_out;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;
uniform mat3 normalMatrix;

uniform vec3 cameraPosition;

uniform int textureScale;
uniform int rotateTexture;
uniform int inverseNormal;

void main() {
    data_out.position = vec3(model * vec4(position, 1.0f));
    data_out.texCoord = texCoord * textureScale;

    if (rotateTexture == 1)
        data_out.texCoord = vec2(data_out.texCoord.y, data_out.texCoord.x);

    if (inverseNormal == 1)
        data_out.normal = vec3(normalMatrix * -normal);

    else
        data_out.normal = vec3(normalMatrix * normal);

    data_out.cameraPosition = cameraPosition;
    data_out.proj = proj;
    data_out.view = view;
    data_out.model = model;
    gl_Position = proj * view * vec4(data_out.position, 1.0f);
}