void draw_rectangle_at_offset(rectangle@ r, float x, float y) {
  scene @g = get_scene();
  g.draw_rectangle_world(20, 20, x + r.left(), y + r.top(), x + r.right(), y + r.bottom(), 0, 0xFFFF0000);
}