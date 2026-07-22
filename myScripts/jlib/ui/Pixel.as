/*
 * Pixel class to define a custom pixel size and color
 */
class Pixel {
  Rect rect;
  uint color;

  Pixel(Rect r, uint c) {
    rect = r;
    color = c;
  }
}