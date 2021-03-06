#version 120

// Declare an attribute (in practice parameter) that can be used
// from the outside to control the behavior of the shader
attribute vec4 somePosition;

// Declare an attribute that can be used from the outside to specify
// the normal of a vertex being drawn
attribute vec4 inputNormal;

// Use a constant color for all vertices (will be modified by 
// light position)
uniform vec3 inputColor = vec3(1.0, 0.3, 0.3);

// Settings related to light
uniform vec4 lampPosition = vec4(-1.0, 1.0, -1.0, 1.0);
uniform float specularHardness = 6.0;
uniform float specularStrength = 0.2;
uniform float diffuseStrength = 0.8;
uniform float ambientStrength = 0.2;

// Declare a semi-constant for rotating the vertex positions (around 
// origin). We give the default of no rotation.
uniform vec3 objectRotation = vec3(0.0, 0.0, 0.0);

// Declare a semi-constant for scaling the vertex positions to fit the
// viewport. We give a default value of "no scaling" (all is 1.0).
uniform vec4 viewportScaling = vec4(1.0, 1.0, 1.0, 1.0);

// View normal. The default value is that it's frontal.
uniform vec4 viewNormal = vec4(0.0, 0.0, -1.0, 1.0);

// for forwarding to fragment shader
varying vec4 outputColor;
varying vec4 outViewNormal;
varying vec4 outVertexNormal;
varying vec4 outLightDirection;
varying float outSpecularHardness;
varying float outSpecularStrength;


void main() {

  vec3 angles = radians(objectRotation);
  vec3 c = cos(angles);
  vec3 s = sin(angles);

  mat4 rx = mat4( 1.0,  0.0,  0.0,  0.0,
                  0.0,  c.x,  s.x,  0.0,
                  0.0, -s.x,  c.x,  0.0,
                  0.0,  0.0,  0.0,  1.0);

  mat4 ry = mat4( c.y,  0.0, -s.y,  0.0,
                  0.0,  1.0,  0.0,  0.0,
                  s.y,  0.0,  c.y,  0.0,
                  0.0,  0.0,  0.0,  1.0);

  mat4 rz = mat4( c.z, -s.z,  0.0,  0.0,
                  s.z,  c.z,  0.0,  0.0,
                  0.0,  0.0,  1.0,  0.0,
                  0.0,  0.0,  0.0,  1.0);

  // Transform vertex world coordinates to account for rotation
  // around origin. 
  vec4 rotatedCoordinates = rz * ry * rx * somePosition;

  // Finally multiply it with scaling in order to compensate for window size.
  gl_Position = viewportScaling * rotatedCoordinates;

  // We also need to rotate normals
  vec4 rotatedNormal = rz * ry * rx * inputNormal;

  // Normalization turns the vectors 1.0 long, in the same direction
  vec4 normalizedRotatedNormal = normalize(rotatedNormal);
  vec4 normalizedLightDirection = normalize(lampPosition);

  // Calculate cos(angle) for the angle between the normal and the light direction
  float dotProduct = dot(normalizedRotatedNormal, normalizedLightDirection);

  // the dotProduct can be negative, so clamp those values to 0
  float diffuseLightCoefficient = max(0.0, dotProduct);

  // Calculate the diffuse light contribution to the overall color
  vec3 diffuseColors = inputColor * diffuseLightCoefficient * diffuseStrength;

  // Calculate an ambient contribution to the overall color
  vec3 ambientColors = inputColor * ambientStrength;

  // Add all (vertex shader) light contributions together. Specular
  // light is calculated in the fragment shader
  vec3 colors = diffuseColors + ambientColors;
  
  // Convert to a vec4 
  vec4 modifiedColor = vec4(colors, 1.0);

  // Pass on the resulting color to the fragment shader
  outputColor = modifiedColor;

  // Forward uniform settings
  outSpecularHardness = specularHardness;
  outSpecularStrength = specularStrength;

  // Forward calculated variables 
  outViewNormal = viewNormal;
  outVertexNormal = normalizedRotatedNormal;
  outLightDirection = normalizedLightDirection;
}

