// Declare an attribute that can be used from the outside to control 
// the behavior of the shader, in this case the location of a vertex
attribute vec4 somePosition;

void main() {
  // Use the declared attribute to control the location of the
  // vertex currently being drawn
  gl_Position = somePosition;
}

