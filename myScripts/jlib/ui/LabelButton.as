#include "../../../lib/ui/Button.cpp"
#include "../../../lib/ui/label.cpp"
class LabelButton : ButtonClickHandler, callback_base {
  private float SIZE = 10;
  //Button
  UI@ ui;
  scene@ g;
  Button@ button;
  Mouse@ mouse;
  Rect border;
  string callback;

  LabelButton(UI@ ui, float X1, float Y1, string callback_name, string labelText, float inHeight = 34) {
    @g = get_scene();
    @this.ui = ui;
    @this.mouse = ui.mouse;

    border = Rect(X1, Y1, X1 + SIZE, Y1 + SIZE);
    const float height = inHeight - ui.padding * 2;
    @button = Button(ui, Label(ui, labelText));
    button.fit_to_height(height);
    @button.click_listener = this;
    callback = callback_name;
  }


  void draw(bool drawBorder, bool drawBackground) {
    if(button.is_mouse_over) {
      update_label_colour(0xFFFFFF00);
    } else {
      update_label_colour(0xFFFFFFFF);
    }
    button.draw(g, getRect(), drawBorder, drawBackground);
  }

  void draw() {
    button.draw(g, getRect(), true, true);
  }

  void step() {
    button.update(g, getRect());
  }

  void update_label_colour(uint colour) {
    cast<Label@>(button.icon).update_text_colour(colour);
  }

  Rect@ getButtonRect() {
    const float PADDING = ui.padding;
    Rect rect = border;
    rect.set(
      rect.x1 - PADDING - button.width, rect.y1,
      rect.x1 - PADDING, rect.y2);

    return rect;
  }

  /*
   * Returns the bounding rectangle of the button
   */
  Rect getRect() {
    const float PADDING = ui.padding;
    return Rect(border.x1 - PADDING - button.width, border.y1,
      border.x1 - PADDING-1, border.y2+button.height-PADDING-5.5);
  }

  void on_button_click(Button@ button) {
    message@ msg = create_message();
    msg.set_string(callback, "true");
    broadcast_message(callback, msg); 
  }
}