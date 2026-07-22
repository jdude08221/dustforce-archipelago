class Vec3
{
  scene@ g;
  float x, y, z;
  float size = 10;
  Vec3(float x=0, float y=0, float z=0)
  {
    @g = get_scene();
    this.x = x;
    this.y = y;
    this.z = z;
  }
  
  float magnitude()
  {
    return sqrt(x * x + y * y + z * z);
  }
  
  float sqr_magnitude()
  {
    return x * x + y * y + z * z;
  }
  
  void normalise()
  {
    float length = sqrt(x * x + y * y);
    
    if(length != 0)
    {
      x /= length;
      y /= length;
      z /= length;
    }
    else
    {
      x = y = z = 0;
    }
  }
  
  bool opEquals(const Vec3 &in other)
  {
    return x == other.x && y == other.y && z == other.z;
  }
  
  Vec3@ opDivAssign(const float &in v)
  {
    if(v != 0)
    {
      x /= v;
      y /= v;
    }
    else
    {
      x = y = 0;
    }
    
    return this;
  }
  
  Vec3@ opMulAssign(const float &in v)
  {
    x *= v;
    y *= v;
    z *= v;
    return this;
  }
  
  bool equals(const float &in x, const float &in y, const float &in z = 0)
  {
    return this.x == x && this.y == y && this.z == z;
  }
  
  void set(const float &in x, const float &in y, const float &in z = 0)
  {
    this.x = x;
    this.y = y;
    this.z = z;
  }
  
  void set(const Vec3 &in v)
  {
    x = v.x;
    y = v.y;
    z = v.z;
  }

  float dot(Vec3 b) {
   float product = 0;
   product += x * b.x;
   product += y * b.y;
   product += z * b.z;
   return product;
  }

  void print() {
    puts("Vec3: x " + x + " y " + y + " z " + z);
  }

  void draw(float offsetX, float offsetY, float layer = 20, float sublayer = 19) {
      g.draw_rectangle_world(layer, sublayer, x - size/2 + offsetX, y - size/2 + offsetY,
      x + size/2 + offsetX,  y + size/2 + offsetY, 0, 0xFFFFFFFF);
  }
}