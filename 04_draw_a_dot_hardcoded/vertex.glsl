#version 120

void main() {
  // Specify a single vertex at the center of the coordinate system
  gl_Position = vec4(0.0, 0.0, 0.0, 1.0);

  // Specify that points are 10 pixels large
  gl_PointSize = 10.0;
}

