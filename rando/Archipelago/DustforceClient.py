from __future__ import annotations
import os
import sys
import time
import asyncio
import typing
import bsdiff4
import shutil

import Utils

from NetUtils import NetworkItem, ClientStatus
from worlds import undertale
from MultiServer import mark_raw
from CommonClient import CommonContext, server_loop, \
    gui_enabled, ClientCommandProcessor, logger, get_base_parser
from Utils import async_start

# Heartbeat for position sharing via bounces, in seconds
UNDERTALE_STATUS_INTERVAL = 30.0
UNDERTALE_ONLINE_TIMEOUT  = 60.0

class DustforceCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_resync(self):
        """Manually trigger a resync."""
        if isinstance(self.ctx, DustforceContext):
            self.output(f"Syncing items.")
            self.ctx.syncing = True

    def _cmd_savepath(self, directory: str):
        """Redirect to proper save data folder. This is necessary for Linux users to use before connecting."""
        if isinstance(self.ctx, DustforceContext):
            self.ctx.dustmod_path = directory
            self.output("Changed to the following directory: " + self.ctx.dustmod_path)

    def _cmd_deathlink(self):
        """Toggles deathlink"""
        if isinstance(self.ctx, DustforceContext):
            self.ctx.deathlink_status = not self.ctx.deathlink_status
            if self.ctx.deathlink_status:
                self.output(f"Deathlink enabled.")
            else:
                self.output(f"Deathlink disabled.")


class DustforceContext(CommonContext):
    tags = {"AP", "Online"}
    game = "Dustforce"
    command_processor = DustforceCommandProcessor
    items_handling = 0b111
    route = None
    pieces_needed = None
    completed_routes = None
    completed_count = 0
    dustmod_path = None
    splitstxtcleared = False
    splittxt_last_modified = 0
    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.pieces_needed = 0
        self.finished_game = False
        self.game = "Dustforce"
        self.got_deathlink = False
        self.syncing = False
        self.deathlink_status = False
        self.tem_armor = False
        self.completed_count = 0
        self.completed_routes = {"pacifist": 0, "genocide": 0, "neutral": 0}
        self.last_sent_position: typing.Optional[tuple] = None
        self.last_room: typing.Optional[str] = None
        self.last_status_write: float = 0.0
        self.other_undertale_status: dict[int, dict] = {}


    def patch_game(self):
        return
        #TODO: no patches required for df at this moment
        # return
        # with open(Utils.user_path("Dustforce", "data.win"), "rb") as f:
        #     patchedFile = bsdiff4.patch(f.read(), undertale.data_path("patch.bsdiff"))
        # with open(Utils.user_path("Dustforce", "data.win"), "wb") as f:
        #     f.write(patchedFile)
        # os.makedirs(name=Utils.user_path("Dustforce", "Custom Sprites"), exist_ok=True)
        # with open(os.path.expandvars(Utils.user_path("Dustforce", "Custom Sprites",
        #                              "Which Character.txt")), "w") as f:
        #     f.writelines(["// Put the folder name of the sprites you want to play as, make sure it is the only "
        #                   "line other than this one.\n", "frisk"])
        #     f.close()

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def clear_dustforce_files(self):
        #TODO: clean up splits.txt and plugin files if they exist
        print("NOT IMPLEMENTED")

    async def connect(self, address: typing.Optional[str] = None):
        #Overload you can use if needed
        await super().connect(address)

    async def disconnect(self, allow_autoreconnect: bool = False):
        self.clear_dustforce_files()
        await super().disconnect(allow_autoreconnect)

    async def connection_closed(self):
        self.clear_dustforce_files()
        await super().connection_closed()

    async def shutdown(self):
        self.clear_dustforce_files()
        await super().shutdown()

    def update_online_mode(self, online):
        old_tags = self.tags.copy()
        if online:
            self.tags.add("Online")
        else:
            self.tags -= {"Online"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            async_start(self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}]))

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.game = self.slot_info[self.slot].game
        async_start(process_undertale_cmd(self, cmd, args))

    def run_gui(self):
        from kvui import GameManager

        class UTManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Dustforce Client"

        self.ui = UTManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")
        open_dustforce_find_window(self)
        #TODO: this should not be here probably. I'm sure there is some async way to do it
        asyncio.create_task(launch_dustforce(os.path.join(self.dustmod_path, "dustmod.exe")))  # Launch the game with the selected path

    def on_deathlink(self, data: typing.Dict[str, typing.Any]):
        self.got_deathlink = True
        super().on_deathlink(data)


def to_room_name(place_name: str):
    if place_name == "Old Home Exit":
        return "room_ruinsexit"
    elif place_name == "Snowdin Forest":
        return "room_tundra1"
    elif place_name == "Snowdin Town Exit":
        return "room_fogroom"
    elif place_name == "Waterfall":
        return "room_water1"
    elif place_name == "Waterfall Exit":
        return "room_fire2"
    elif place_name == "Hotland":
        return "room_fire_prelab"
    elif place_name == "Hotland Exit":
        return "room_fire_precore"
    elif place_name == "Core":
        return "room_fire_core1"


async def process_undertale_cmd(ctx: DustforceContext, cmd: str, args: dict):
    print(f"Received command: {cmd} with args: {args}")
    if cmd == "Connected":
        if not os.path.exists(ctx.dustmod_path):
            os.mkdir(ctx.dustmod_path)
        #ctx.route = args["slot_data"]["route"]

        if any(info.game == "Dustforce" and slot != ctx.slot 
               for slot, info in ctx.slot_info.items()):
            ctx.set_notify("dustforce_room_status")

        filename = f"check.spot"
        #TODO: update to write to some file to update what has been done in game
        # with open(os.path.join(ctx.dustmod_path, filename), "a") as f:
        #     for ss in set(args["checked_locations"]):
        #         f.write(str(ss-12000)+"\n")
        #     f.close()
    elif cmd == "LocationInfo":
        #TODO: provide giving hints based on current location
        print("not implemented")
        # for l in args["locations"]:
        #     locationid = l.location
        #     filename = f"{str(locationid-12000)}.hint"
        #     with open(os.path.join(ctx.dustmod_path, filename), "w") as f:
        #         toDraw = ""
        #         for i in range(20):
        #             if i < len(str(ctx.item_names.lookup_in_game(l.item))):
        #                 toDraw += str(ctx.item_names.lookup_in_game(l.item))[i]
        #             else:
        #                 break
        #         f.write(toDraw)
        #         f.close()
    elif cmd == "Retrieved":
        if str(ctx.slot)+" RoutesDone neutral" in args["keys"]:
            if args["keys"][str(ctx.slot)+" RoutesDone neutral"] is not None:
                ctx.completed_routes["neutral"] = args["keys"][str(ctx.slot)+" RoutesDone neutral"]
        if str(ctx.slot)+" RoutesDone genocide" in args["keys"]:
            if args["keys"][str(ctx.slot)+" RoutesDone genocide"] is not None:
                ctx.completed_routes["genocide"] = args["keys"][str(ctx.slot)+" RoutesDone genocide"]
        if str(ctx.slot)+" RoutesDone pacifist" in args["keys"]:
            if args["keys"][str(ctx.slot) + " RoutesDone pacifist"] is not None:
                ctx.completed_routes["pacifist"] = args["keys"][str(ctx.slot)+" RoutesDone pacifist"]
        if "undertale_room_status" in args["keys"] and args["keys"]["undertale_room_status"]:
            status = args["keys"]["undertale_room_status"]
            ctx.other_undertale_status = {
                int(key): val for key, val in status.items()
                if int(key) != ctx.slot
            }
    elif cmd == "SetReply":
        if args["value"] is not None:
            if str(ctx.slot)+" RoutesDone pacifist" == args["key"]:
                ctx.completed_routes["pacifist"] = args["value"]
            elif str(ctx.slot)+" RoutesDone genocide" == args["key"]:
                ctx.completed_routes["genocide"] = args["value"]
            elif str(ctx.slot)+" RoutesDone neutral" == args["key"]:
                ctx.completed_routes["neutral"] = args["value"]
        if args.get("key") == "undertale_room_status" and args.get("value"):
            ctx.other_undertale_status = {
                int(key): val for key, val in args["value"].items()
                if int(key) != ctx.slot
            }
    elif cmd == "ReceivedItems":
        start_index = args["index"]

        if start_index == 0:
            ctx.items_received = []
        elif start_index != len(ctx.items_received):
            await ctx.check_locations(ctx.locations_checked)
            await ctx.send_msgs([{"cmd": "Sync"}])

        if start_index == len(ctx.items_received):
          for item in args["items"]:
              ctx.items_received.append(NetworkItem(*item))

          # Count each key type across everything received so far
          counts = {"bronze": 0, "silver": 0, "gold": 0, "red": 0}
          for net_item in ctx.items_received:
              name = ctx.item_names.lookup_in_game(net_item.item)
              key_type = key_type_for_item(name)
              if key_type in counts:
                  counts[key_type] += 1

          path = ctx.dustmod_path
          sav_path = os.path.join(path, "content", "plugins", "embeds", "archipelago.sav")
          with open(sav_path, "w") as file:   # "w" truncates cleanly, no leftover bytes
              file.write(f"keys,{counts['bronze']},{counts['silver']},{counts['gold']},{counts['red']}")

          ctx.watcher_event.set()

    elif cmd == "RoomUpdate":
        if "checked_locations" in args:
            print("not implemented")
            #TODO: I have no idea what this is for but might need it
            # filename = f"check.spot"
            # with open(os.path.join(ctx.dustmod_path, filename), "a") as f:
            #     for ss in set(args["checked_locations"]):
            #         f.write(str(ss-12000)+"\n")
            #     f.close()

    elif cmd == "Bounced":
        data = args.get("data", {})
        if "x" in data and "room" in data:
            print("not implemented")
            #TODO: no idea what this is for but implement.
            # if data["player"] != ctx.slot and data["player"] is not None:
            #     filename = f"FRISK" + str(data["player"]) + ".playerspot"
            #     with open(os.path.join(ctx.dustmod_path, filename), "w") as f:
            #         f.write(str(data["x"]) + str(data["y"]) + str(data["room"]) + str(
            #             data["spr"]) + str(data["frm"]))
            #         f.close()


#TODO: This is pretty placeholder. We should think of better logic. Open to ideas
def key_type_for_item(item_name: str):
    """Map a received item name to its dustmod key type, or None."""
    mapping = {
        "Downhill Key": "bronze",
        "Shaded Grove Key": "bronze",
        "Dahlia Key": "bronze",
        "Valley Key": "silver",
        "Firefly Forest Key": "silver"
        # ...fill in the rest...
    }
    return mapping.get(item_name)

async def multi_watcher(ctx: DustforceContext):
    #TODO: might be fun to have multiplayer but for sure a stretch goal
    return
    # while not ctx.exit_event.is_set():
    #     if "Online" in ctx.tags and any(
    #             info.game == "Dustforce" and slot != ctx.slot
    #             for slot, info in ctx.slot_info.items()):
    #         now = time.time()
    #         path = ctx.dustmod_path
    #         for root, dirs, files in os.walk(path):
    #             for file in files:
    #                 if "spots.mine" in file:
    #                     with open(os.path.join(root, file), "r") as mine:
    #                         this_x = mine.readline()
    #                         this_y = mine.readline()
    #                         this_room = mine.readline()
    #                         this_sprite = mine.readline()
    #                         this_frame = mine.readline()

    #                     if this_room != ctx.last_room or \
    #                             now - ctx.last_status_write >= UNDERTALE_STATUS_INTERVAL:
    #                         ctx.last_room = this_room
    #                         ctx.last_status_write = now
    #                         await ctx.send_msgs([{
    #                             "cmd": "Set",
    #                             "key": "undertale_room_status",
    #                             "default": {},
    #                             "want_reply": False,
    #                             "operations": [{"operation": "update",
    #                                             "value": {str(ctx.slot): {"room": this_room,
    #                                                                        "time": now}}}]
    #                         }])

    #                     # If player was visible but timed out (heartbeat) or left the room, remove them.
    #                     for slot, entry in ctx.other_undertale_status.items():
    #                         if entry.get("room") != this_room or \
    #                                 now - entry.get("time", now) > UNDERTALE_ONLINE_TIMEOUT:
    #                             playerspot = os.path.join(ctx.dustmod_path,
    #                                                       f"FRISK{slot}.playerspot")
    #                             if os.path.exists(playerspot):
    #                                 os.remove(playerspot)

    #                     current_position = (this_x, this_y, this_room, this_sprite, this_frame)
    #                     if current_position == ctx.last_sent_position:
    #                         continue

    #                     # Empty status dict = no data yet → send to bootstrap.
    #                     online_in_room = any(
    #                         entry.get("room") == this_room and
    #                         now - entry.get("time", now) <= UNDERTALE_ONLINE_TIMEOUT
    #                         for entry in ctx.other_undertale_status.values()
    #                     )
    #                     if ctx.other_undertale_status and not online_in_room:
    #                         continue

    #                     message = [{"cmd": "Bounce", "games": ["Dustforce"],
    #                                 "data": {"player": ctx.slot, "x": this_x, "y": this_y,
    #                                          "room": this_room, "spr": this_sprite,
    #                                          "frm": this_frame}}]
    #                     await ctx.send_msgs(message)
    #                     ctx.last_sent_position = current_position

    #     await asyncio.sleep(0.1)

def open_dustforce_find_window(self):
  import tkinter as tk
  from tkinter import filedialog
  from tkinter import messagebox

  # Create an invisible Tkinter root window
  root = tk.Tk()
  root.withdraw()

  # Open the file picker and get the absolute path
  file_path = filedialog.askopenfilename(
      title="Select dustmod.exe",
      filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
  )

  if file_path:
      print(f"Selected file: {file_path}")
      self.dustmod_path = os.path.dirname(file_path)
      
  else:
      # Open the Confirm / Cancel window
      result = messagebox.askokcancel("Dustmod.exe Not Found", "Invalid dustforce path detected. A valid path to dustmod.exe is required for Archipelago to work with Dustforce.\nDo you want to try selecting the file again?", icon="warning")

      if result:
          open_dustforce_find_window(self)  # Call the function again to open the file picker
      else:
          print("File selection cancelled. Archipelago will not work without a valid dustmod.exe path.")
          #TODO: handle user selecting cancel

def is_ss(splitstxtline):
    return  splitstxtline[1] == "0" and splitstxtline[2] == "100"
    
def splits_to_location(level):
    if level == "downhill":
        return 1
    elif level == "shadedgrove":
        return 2
    elif level == "valley":
        return 3
    elif level == "fireflyforest":
        return 4
    elif level == "dahlia":
        return 5
    elif level == "tunnels":
        return 6
    elif level == "fields":
        return 7

async def update_location_ss(ctx: DustforceContext, level_str: str):
    await ctx.check_locations([splits_to_location(level_str)])

async def update_state_from_splittxt(ctx: DustforceContext,path: str):
  # Ensure we only read split.txt when its updated
  file_path = os.path.join(path, "split.txt")
  timestamp = 0
  if os.path.exists(file_path):
      timestamp = os.stat(file_path).st_mtime
  else:
      print("File not found.")

  if(ctx.splittxt_last_modified == timestamp):
      return
  
  #print(f"Update: {ctx.splittxt_last_modified} {timestamp}")
  ctx.splittxt_last_modified = timestamp
  
  # Read split.txt file contents
  try:
    with open(file_path, "r") as f:
      lines = f.readlines()
      if len(lines) > 1:
        ln = lines[1]
        if len(ln) > 2:
          split_line = ln.split()
          if is_ss(split_line):
            await update_location_ss(ctx, split_line[0])

  except Exception as e:
      print("Exception when processing split.txt")
    
async def game_watcher(ctx: DustforceContext):
    while not ctx.exit_event.is_set():
        path = ctx.dustmod_path
        # Clear split.txt when dustmod path is available
        if not ctx.splitstxtcleared and path != None:
          with open(os.path.join(path,"split.txt"), "w") as f:
            pass
          with open(os.path.join(path,"output.log"), "w") as f:
            #TODO: we need to ensure if the archipelago client closes, we somehow persist the 
            #log data otherwise this will wipe it out. Not really sure how to handle it other 
            #than just writing it all to a file on disk. For now its ephemeral
            pass
          with open(os.path.join(path, "content", "plugins", "embeds", "archipelago.sav"), "w") as f:
              f.write("keys,0,0,0,0")
          ctx.splitstxtcleared = True
        
        await ctx.update_death_link(ctx.deathlink_status)

        if ctx.syncing:
            print("not implemented")
            # for root, dirs, files in os.walk(path):
            #     for file in files:
            #         if ".item" in file:
            #             os.remove(os.path.join(root, file))
            # await ctx.check_locations(ctx.locations_checked)
            # await ctx.send_msgs([{"cmd": "Sync"}])

            ctx.syncing = False
        if ctx.got_deathlink:
            print("not implemented")
            #TODO: handle deathlink
            # ctx.got_deathlink = False
            # with open(os.path.join(ctx.dustmod_path, "WelcomeToTheDead.youDied"), "w") as f:
            #     f.close()
        sending = []
        victory = False
        found_routes = 0
        #JDUDE WORKING HERE
        await update_state_from_splittxt(ctx, path)

        try:
          with open(os.path.join(path, "content", "plugins", "embeds", "archipelago.sav"), "r") as f:
            for line in f:
                continue
        except Exception as e:
            print("Exception when processing plugin file")

        try:
          with open(os.path.join(path, "output.log"), "r") as f:
            for line in f:
                #print("Output Log " + line)
                continue
        except Exception as e:
            print("Exception when processing output.log")

        #TODO: Undertale code.... idk remove eventually. Keeping it in case I want to refrence it
        # for root, dirs, files in os.walk(path):
        #     for file in files:
        #         if "DontBeMad.mad" in file:
        #             os.remove(os.path.join(root, file))
        #             if "DeathLink" in ctx.tags:
        #                 await ctx.send_death()
        #         if "scout" == file:
        #             sending = []
        #             try:
        #                 with open(os.path.join(root, file), "r") as f:
        #                     lines = f.readlines()
        #                 for l in lines:
        #                     if ctx.server_locations.__contains__(int(l)+12000):
        #                         sending = sending + [int(l.rstrip('\n'))+12000]
        #             finally:
        #                 await ctx.send_msgs([{"cmd": "LocationScouts", "locations": sending,
        #                                                   "create_as_hint": int(2)}])
        #                 os.remove(os.path.join(root, file))
        #         if "check.spot" in file:
        #             sending = []
        #             try:
        #                 with open(os.path.join(root, file), "r") as f:
        #                     lines = f.readlines()
        #                 for l in lines:
        #                     sending = sending+[(int(l.rstrip('\n')))+12000]
        #             finally:
        #                 await ctx.check_locations(sending)
        #         if "victory" in file and str(ctx.route) in file:
        #             victory = True
        #         if ".playerspot" in file and "Online" not in ctx.tags:
        #             os.remove(os.path.join(root, file))
        #         if "victory" in file:
        #             if str(ctx.route) == "all_routes":
        #                 if "neutral" in file and ctx.completed_routes["neutral"] != 1:
        #                     await ctx.send_msgs([{"cmd": "Set", "key": str(ctx.slot)+" RoutesDone neutral",
        #                                           "default": 0, "want_reply": True, "operations": [{"operation": "max",
        #                                                                                             "value": 1}]}])
        #                 elif "pacifist" in file and ctx.completed_routes["pacifist"] != 1:
        #                     await ctx.send_msgs([{"cmd": "Set", "key": str(ctx.slot)+" RoutesDone pacifist",
        #                                           "default": 0, "want_reply": True, "operations": [{"operation": "max",
        #                                                                                             "value": 1}]}])
        #                 elif "genocide" in file and ctx.completed_routes["genocide"] != 1:
        #                     await ctx.send_msgs([{"cmd": "Set", "key": str(ctx.slot)+" RoutesDone genocide",
        #                                           "default": 0, "want_reply": True, "operations": [{"operation": "max",
        #                                                                                             "value": 1}]}])
        # if str(ctx.route) == "all_routes":
        #     found_routes += ctx.completed_routes["neutral"]
        #     found_routes += ctx.completed_routes["pacifist"]
        #     found_routes += ctx.completed_routes["genocide"]
        # if str(ctx.route) == "all_routes" and found_routes >= 3:
        #     victory = True
        # ctx.locations_checked = sending
        # if (not ctx.finished_game) and victory:
        #     await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
        #     ctx.finished_game = True
        await asyncio.sleep(0.1)


def main():
    Utils.init_logging("DustforceClient", exception_logger="Client")
    splitstxtcleared = False
    async def _main():
        ctx = DustforceContext(None, None)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        
        asyncio.create_task(
            game_watcher(ctx), name="DustforceProgressionWatcher")
        
        asyncio.create_task(
            multi_watcher(ctx), name="DustforceMultiplayerWatcher")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    import colorama

    colorama.just_fix_windows_console()

    asyncio.run(_main())
    colorama.deinit()

async def launch_dustforce(path: str):
    import asyncio
    import sys
    import os

    try:
        process = await asyncio.create_subprocess_exec(
            path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )

        await process.wait()
        print(f"[dustmod] exited with code {process.returncode}")

    except FileNotFoundError:
        print(f"Error: Could not find the file at {path}. Check the path spelling.")
    except PermissionError:
        print(f"Access Denied: Try running your IDE/Python terminal as Administrator.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = get_base_parser(description="Dustforce Client, for text interfacing.")
    args = parser.parse_args()
    main()
