#version 120

// This color is fetched from the vertex shader. Note that
// there is a "varying" with the same name there. This causes
// the variables to be connected automatically without us 
// having to say so in the python code
varying vec4 outputColor;

varying vec4 outViewNormal;
varying vec4 outVertexNormal;
varying vec4 outLightDirection;

void main() {

  // Calculate reflected light normal
  vec4 reflectionNormal = reflect(-outLightDirection, outVertexNormal);

  // Specular contribution. This model needs to be improved. 

  float specularCos = max(0.0, dot(reflectionNormal, outViewNormal));

  float specularLightCoefficient = max(0.0, min(1.0, pow(specularCos,4.0)) - 0.4);
  vec4 specularColors = outputColor * specularLightCoefficient;
  vec4 colors = specularColors + outputColor;

  vec4 modifiedColor = vec4(min(1.0, colors.r), min(1.0, colors.g), min(1.0, colors.b), 1.0);

  // Set the color of the currently drawn pixel. If the pixel
  // coincide with a vertex position, the exact color specified
  // for that vertex is used. If the pixel is somewhere else, the
  // color is interpolated between the nearest vertices' colors.
  gl_FragColor = modifiedColor;
}

