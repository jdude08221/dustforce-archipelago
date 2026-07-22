class SpriteConfig {
  [text] bool draw_sprite = true;
  [slider,min:-15,max:15] float scalex = 1;
  [slider,min:-15,max:15] float scaley = 1;
  [slider,min:0,max:255] uint opacity = 255;
  [text] int layer = 18;
  [text] int sublayer = 18;
  [position,mode:world,layer:=layer.3,y:Y1] float X1;
  [hidden] float Y1;
  [angle] float rotation; 
  [text] float wobble = 10;
  [text] float speed = 100;
  [hidden] string spriteName = "";
  sprites@ spr = null;
  rectangle@ spr_rect = null;
  float theta = 0;
  float update_frame = 0;
  float xofs = 0;
  float yofs = 0;

  float xposofs = 0;
  float yposofs = 0;

  scene@ g;
  SpriteConfig() {
    @g = get_scene();
  }

  void init(string name, sprites@ s, bool move = true) {
    spriteName = name;
    @spr = @s;
    @spr_rect = s.get_sprite_rect(name, 0);
    xposofs = scalex * (spr_rect.left() + spr_rect.right())/2;
    yposofs = scaley* (spr_rect.top() + spr_rect.bottom())/2;

    if(move && theta == 0) {
      srand(get_time_us());
      theta = rand();
    }
  }

  void draw() {
    if(!draw_sprite || spriteName == "" || @spr == null) {
      return;
    }@spr_rect = spr.get_sprite_rect(spriteName, 0);
    //void draw_rectangle_world(uint layer, uint sub_layer, float x1, float y1, float x2, float y2, float rotation, uint colour);
    //g.draw_rectangle_world(layer,sublayer,spr_rect.left()*scalex *3, spr_rect.top()*scaley*3, spr_rect.right()*scalex*3, spr_rect.bottom()*scaley*3, rotation, 0x50FFFFFF);
    spr.draw_world(layer, sublayer, spriteName, 0, 1, X1 + xofs - xposofs, Y1 + yofs - yposofs, rotation, scalex , scaley, 0x00FFFFFF + (opacity << 24));
  }

  void update() {
    update_frame++;

    xofs = wobble * cos(theta);
    yofs = wobble * sin(theta);
    theta = (theta + (speed * 3.14159 / 180) / 30) % (3.14159 * 2);
  }
}