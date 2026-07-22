#include "../myScripts/jlib/entities/entity_helpers.as"
#include "../myScripts/jlib/const/df_consts.as"
#include "../myScripts/jlib/drawing/DrawRect.as"
//#include "../myScripts/unsorted/readvars.as"

const string EMBED_KEY = "archipelago.sav";
const string EMBED_FILE = "archipelago.sav";

//TODO: have heartbeat set up to ensure python client is running. If it is not, we can run into some bad desyncs

// varstruct door_set on a door does remember what type of key door it was.
class script {
  scene@ g;
  string current_nexus = "none";
  nexus_api@ n;
  rectangle@ r;
  bool in_main_nexus = false;
  array<entity@> doors;

  //Store keys used last step
  int last_wood, last_silver, last_gold, last_red = 0;
  int last_score_count;
  //readvars rv;

  script() {
    @g = get_scene();
    last_score_count = 0;
  }

  void step(int entities) {

    if(!in_main_nexus) {
     in_main_nexus = g.map_filename() == "Nexus DX";
     @n = get_nexus_api();
     if(@n == null) {
      in_main_nexus = false;
      return;
     }
     if(in_main_nexus) update_client("In Main Nexus");
    }

    
    //step_rando(entities);
  }

  void step_post(int entities) {
    update_keys();
  }

  void update_keys() {
    // While we are not in a randomizer nexus, do not update key counts in game
    load_embed(EMBED_KEY, EMBED_FILE);
    string line = get_embed_value(EMBED_KEY);
    string keys = line.split("\n")[0];
    array<string> key_vals = keys.split(",");

    if(key_vals[0] != "keys") return; //File was corrupted or modified manually.
    
    // These are the "true" value of keys we have in our possession
    int wood = parseInt(key_vals[1]);
    int silver = parseInt(key_vals[2]);
    int gold = parseInt(key_vals[3]);
    int red = parseInt(key_vals[4]);


    // Print to console so python client can see the player used a key.
    if (last_wood > wood) {
      update_client("wood_used");
    } else if(last_wood < wood) {
      update_client("wood_recieved");
    }

    if (last_silver > silver) {
      update_client("silver_used");
    } else if(last_silver < silver) {
      update_client("silver_recieved");
    }

    if (last_gold > gold) {
      update_client("gold_used");
    } else if(last_gold < gold) {
      update_client("gold_recieved");
    }

    if (last_red > red) {
      update_client("red_used");
    } else if(last_red < red) {
      update_client("red_recieved");
    }
    
    last_wood = wood;
    last_silver = silver;
    last_gold = gold;
    last_red = red;

    int sc = n.score_count();

    if(last_score_count != sc) {
      update_client("Door Opened");
      last_score_count = sc;
      // Set all doors to be "none" key type. This ensures no doors give keys
      for(uint i = 0; i < sc; i++) {
        string level = n.score_level(i);

        // bool score_lookup(string level, int &out thorough, int &out finesse, float &out time, int &out key_type)
        int thorough, finesse, key_type;
        float time;
        n.score_lookup(level, thorough, finesse, time, key_type);
        n.score_set(level, thorough, finesse, time, KeyType::None);
      }
    }



    // Key count is calculated by taking all level keys you earned (stored in score_lookup) then subtracting the used keys from that total.
    // By setting the keys to be negative, it will end up adding the key value.
    n.set_keys_used(-wood, -silver, -gold, -red, false);
  }

  void on_level_start() {
    in_main_nexus = false;
  }

  void step_rando(int entites) {
    doors = get_doors_on_screen(get_camera(0));
  }

  void draw(float sub_frame) {
    for(uint i = 0; i < doors.length(); i++) {
      //draw_rectangle_at_offset(doors[i].base_rectangle(), doors[i].x(), doors[i].y());
    }
    
  }

  // Potentially useful future method to determine if we are in a randomizer nexus. For now we are focusing on vanilla.
  bool is_randomizer_nexus() {
    string filename = g.map_filename();
    array<string>@ file = filename.split("\\");
    if(file[0] == filename) return false; // Not an archipelago nexus
    file = filename.split("-");
    if(file[0] != "randomizer") return false;

    return true;
  }

  private array<entity@> get_doors_on_screen(camera@ c) {
    array<entity@> entites = get_entities_on_screen(c);
    array<entity@> ret;
    for(uint i = 0; i < entites.size(); i++) {
      if(entites[i].type_name() == "level_door") {
        ret.insertLast(entites[i]);
      }
    }
    return ret;
  }
}


void update_client(string s) {
  puts("Archipelago_Message: "+s);
}
// downhill
// shadedgrove
// dahlia
// fields
// momentum
// fireflyforest
// tunnels
// momentum2
// suntemple
// ascent
// summit
// grasscave
// den
// autumnforest
// garden
// hyperdifficult
// atrium
// secretpassage
// alcoves
// mezzanine
// cave
// cliffsidecaves
// library
// courtyard
// precarious
// treasureroom
// arena
// ramparts
// moontemple
// observatory
// parapets
// brimstone
// vacantlot
// sprawl
// development
// abandoned
// park
// boxes
// chemworld
// factory
// tunnel
// basement
// scaffold
// cityrun
// clocktower
// concretetemple
// alley
// hideout
// control
// ferrofluid
// titan
// satellite
// vat
// venom
// security
// mary
// wiringfixed
// containment
// orb
// pod
// mary2
// coretemple
// abyss
// dome
// kilodifficult
// megadifficult
// gigadifficult
// teradifficult
// petadifficult
// exadifficult
// zettadifficult
// yottadifficult