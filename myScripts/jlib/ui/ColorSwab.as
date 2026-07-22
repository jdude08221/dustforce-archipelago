
#include '../../../lib/ui/shapes/Shape.cpp';
/*
 * Class that is used with a button to have
 * a colored square be the button contents
 */
class ColorSwab : Shape {
  float thickness;
  uint color;

  ColorSwab(UI@ ui, float thickness = 3, uint color = 0xCCFFFFFF) {
    super(ui, color);
    this.color = color;
    this.thickness = thickness;
  }

  void draw(scene@ g, Rect rect) {
     float centre_x = rect.centre_x;
     float centre_y = rect.centre_y;
     float w = thickness * 0.5;
     g.draw_rectangle_world(17, 20, rect.x1-w, rect.y1-w, rect.x2+w, rect.y2+w, 0, color);
  }
}