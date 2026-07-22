  #include "../const/df_consts.as"
  /**
   * Returns an array of entity handles for all entities close to the given camera's camera. Code stolen and modified some from C's entity outliner.
   * 
   */
  array<entity@> get_entities_on_screen(camera@ cam)
  { 
    float view1_x, view1_y, view1_w, view1_h;
    float view2_x, view2_y, view2_w, view2_h;
    cam.get_layer_draw_rect(0, 19, view1_x, view1_y, view1_w, view1_h);
    cam.get_layer_draw_rect(1, 19, view2_x, view2_y, view2_w, view2_h);

    const float padding_x = 300;
    const float padding_y = 300;
    view1_x -= padding_x; view1_y -= padding_x;
    view2_x -= padding_y; view2_y -= padding_y;
    view1_w += padding_x * 2; view1_h += padding_x * 2;
    view2_w += padding_y * 2; view2_h += padding_y * 2;

    const float view_x1 = min(view1_x, view2_x);
    const float view_y1 = min(view1_y, view2_y);
    const float view_x2 = max(view1_x + view1_w, view2_x + view2_w);
    const float view_y2 = max(view1_y + view1_h, view2_y + view2_h);
    
    array<entity@> ret = add_entities_type(view_y1, view_y2, view_x1, view_x2, ColType::Trigger);
    return ret;
  }

  array<entity@> add_entities_type(const float view_y1, const float view_y2, const float view_x1, const float view_x2, const ColType type)
  {
    scene@ g = get_scene();
    const int count = g.get_entity_collision(view_y1, view_y2, view_x1, view_x2, type);
    array<entity@> ret;
    for(int i = 0; i < count; i++)
    {
      entity@ e = g.get_entity_collision_index(i);
      //puts(c.type_name());
      if(@e != null) {
          ret.insertLast(e);
          //puts(e.type_name()+"");
      }
    }

    return ret;
  }