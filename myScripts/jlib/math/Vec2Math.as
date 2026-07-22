#include "../../lib/math/Vec2.cpp"

//Rotate a vector theta radians
Vec2@ rotate(Vec2@ v, float theta) {
 return Vec2((v.x * cos(theta)) - (v.y * sin(theta)),
             v.x * sin(theta) +  (v.y * cos(theta)));
}