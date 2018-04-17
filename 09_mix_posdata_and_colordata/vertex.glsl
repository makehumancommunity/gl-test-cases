// Declare an attribute that can be used from the outside to control the 
// position of the vertex currently being drawn
attribute vec4 somePosition;

// Declare an attribute that can be used from the outside to control the 
// color of the vertex currently being drawn
attribute vec4 inputColor;

// Declare a connector to the fragment shader (see comment there)
varying vec4 outputColor;

void main() {
  // Use the declared attribute to control the location of the
  // vertex currently being drawn
  gl_Position = somePosition;

  // Fetch the color information we got from the attribute (ie from 
  // python) and simply forward it to the fragment shader via the
  // "outputColor" connector we declared above
  outputColor = inputColor;
}

