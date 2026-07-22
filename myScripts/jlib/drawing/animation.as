class animation {
  int layer, sublayer;
  float x, y;
  array<string> frames;
  bool animating;
  float cur_frame = 0;

  animation(float x_in, float y_in, array<string> f, layer = 18, sublayer = 18) {
    x = x_in;
    y = y_in;
    frames = f;
  }

  void animate() {
    if(!animating) {

    }
  }

}