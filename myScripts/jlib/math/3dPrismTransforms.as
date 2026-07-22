  #include "Matrix.as"

  Matrix@ rotationX(float angle) {
    array<array<float>> rotX = {
    { 1, 0, 0},
    { 0, cos(angle), -sin(angle)},
    { 0, sin(angle), cos(angle)}};
                                
    return Matrix(rotX);
  }

  Matrix@ rotationY(float angle) {
    array<array<float>> rotY = {
    { cos(angle), 0, sin(angle)},
    { 0, 1, 0},
    { -sin(angle), 0, cos(angle)}};
                                
    return Matrix(rotY);
  }

  Matrix@ rotationZ(float angle) {
    array<array<float>> rotZ = { 
      { cos(45 * DEG2RAD), -sin(45 * DEG2RAD), 0},
      { sin(45 * DEG2RAD), cos(45 * DEG2RAD), 0},
      { 0, 0, 1}};
                                
    return Matrix(rotZ);
  }

  Matrix@ projection(float z_distance, float rotatedZ) {
    float z = 1.0/(z_distance - rotatedZ);
    array<array<float>> arrProj = {{1/z, 0.0, 0.0},
                                  {0.0, 1/z, 0.0}};
                              
    return Matrix(arrProj);
  }