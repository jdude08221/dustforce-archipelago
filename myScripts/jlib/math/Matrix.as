//Code taken from https://www.youtube.com/watch?v=tzsgS19RRc8
#include "Vec3.as"
class Matrix {
  //matrix[row][col]
  array<array<float>> vals;

  Matrix(array<array<float>> @m) {
    vals = m;
  }

  Vec3@ multiply(Vec3@ vec) {
    Matrix@ m = vecToMatrix(vec);
    return this.multiply(m);
  }

  Vec3@ multiply(Matrix@ matrixPrime) {
    if(@vals == null || @matrixPrime == null){
      puts("cannot multiply null matrix");
      return null;
    }

    array<array<float>> valsPrime = matrixPrime.vals;
    uint colsA = vals[0].size();
    uint rowsA = vals.size();
    uint colsB = valsPrime[0].size();
    uint rowsB = valsPrime.size();

    Matrix ret(array<array<float>>(rowsA, array<float>(colsB)));
    
    if(colsA != rowsB) {
      return null;
    }

    for(uint i = 0; i < rowsA; i++) {
      for(uint j = 0; j < colsB; j++) {
        float sum = 0;
        for(uint k = 0; k < colsA; k++) {
          sum += (vals[i][k] * valsPrime[k][j]);
        }
        ret.vals[i][j] = sum;
      }
    }
    return matrixToVec3(ret);
  }

  void print() {
    if(@vals == null) {
      puts("matrix is null");
    }
    for(uint i = 0; i < vals.size(); i++) {
      puts("row "+i);
      for(uint j = 0; j < vals[0].size(); j++) {
        puts(vals[i][j] + " ");
      }
    }
  }
}

Matrix@ vecToMatrix(Vec3@ v) {
    Matrix m(array<array<float>>(3, array<float>(1)));
    m.vals[0][0] = v.x;
    m.vals[1][0] = v.y;
    m.vals[2][0] = v.z;
    return m;
  }

Vec3@ matrixToVec3(Matrix@ m) {
  Vec3 v(m.vals[0][0], 
          m.vals[1][0], 
        m.vals.size() > 2 ? m.vals[2][0] : 0);
  return v;
}