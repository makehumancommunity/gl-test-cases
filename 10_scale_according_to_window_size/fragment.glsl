#version 120

// This color is fetched from the vertex shader. Note that
// there is a "varying" with the same name there. This causes
// the variables to be connected automatically without us 
// having to say so in the python code
varying vec4 outputColor;

void main() {
  // Set the color of the currently drawn pixel. If the pixel
  // coincide with a vertex position, the exact color specified
  // for that vertex is used. If the pixel is somewhere else, the
  // color is interpolated between the nearest vertices' colors.
  gl_FragColor = outputColor;
}

