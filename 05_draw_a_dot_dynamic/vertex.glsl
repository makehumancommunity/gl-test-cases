// Declare an attribut (in practice parameter) that can be used
// from the outside to control the behavior of the shader
attribute vec4 somePosition;

void main() {
  // Use the declared attribute to control the location of the
  // vertex currently being drawn
  gl_Position = somePosition;

  // Specify that points are 10 pixels large
  gl_PointSize = 10.0;
}

