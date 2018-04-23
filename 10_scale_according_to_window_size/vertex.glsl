#version 120

// Declare an attribute that can be used from the outside to control the 
// position of the vertex currently being drawn
attribute vec4 somePosition;

// Declare an attribute that can be used from the outside to control the 
// color of the vertex currently being drawn
attribute vec4 inputColor;

// Declare a connector to the fragment shader (see comment there)
varying vec4 outputColor;

// Declare a semi-constant for scaling the vertex positions. A "uniform"
// is given one specific and explicit value in contrast to an "attribute"
// which varies according to which position in a buffer array we're
// currently drawing. We give a default value of "no scaling" (all is 1.0).
uniform vec4 scaling = vec4(1.0, 1.0, 1.0, 1.0);

void main() {
  // Use the declared attribute to control the location of the
  // vertex currently being drawn. In addition we multiply it
  // with scaling in order to compensate for window size.
  gl_Position = somePosition * scaling;

  // Fetch the color information we got from the attribute (ie from 
  // python) and simply forward it to the fragment shader via the
  // "outputColor" connector we declared above
  outputColor = inputColor;
}

