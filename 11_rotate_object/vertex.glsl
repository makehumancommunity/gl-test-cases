// Declare an attribute that can be used from the outside to control the 
// position of the vertex currently being drawn
attribute vec4 somePosition;

// Declare an attribute that can be used from the outside to control the 
// color of the vertex currently being drawn
attribute vec4 inputColor;

// Declare a connector to the fragment shader (see comment there)
varying vec4 outputColor;

// Declare a semi-constant for rotating the vertex positions (around 
// origin). We give the default of no rotation.
uniform vec3 objectRotation = vec3(0.0, 0.0, 0.0);

// Declare a semi-constant for scaling the vertex positions to fit the
// viewport. We give a default value of "no scaling" (all is 1.0).
uniform vec4 viewportScaling = vec4(1.0, 1.0, 1.0, 1.0);

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

  // Fetch the color information we got from the attribute (ie from 
  // python) and simply forward it to the fragment shader via the
  // "outputColor" connector we declared above
  outputColor = inputColor;
}

