#version 120

// This color is fetched from the vertex shader. 
varying vec4 outputColor;

// Values explicitly set by vertex shader
varying vec4 outViewNormal;
varying vec4 outVertexNormal;
varying vec4 outLightDirection;

void main() {

  // Calculate reflected light normal
  vec4 reflectionNormal = reflect(-outLightDirection, outVertexNormal);

  // get cos(angle) for angle between reflected normal and view normal.
  // Clamp it to 0.0, since it might be negative. 
  float specularCos = max(0.0, dot(reflectionNormal, outViewNormal));

  // These lines should be updated once I get a better understanding of 
  // the phong model
  float specularLightCoefficient = max(0.0, min(1.0, pow(specularCos,4.0)) - 0.4);
  vec4 specularColors = outputColor * specularLightCoefficient;
  vec4 colors = specularColors + outputColor;

  // Clamp values higher than 1.0. That should never happen, but doesn't hurt. 
  vec4 modifiedColor = vec4(min(1.0, colors.r), min(1.0, colors.g), min(1.0, colors.b), 1.0);

  // Set the color of the currently drawn pixel. 
  gl_FragColor = modifiedColor;
}

