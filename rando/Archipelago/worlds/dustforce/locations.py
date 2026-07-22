from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import DustforceWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
# Location IDs don't need to be sequential, as long as they're unique and greater than 0.
LOCATION_NAME_TO_ID = {
    "Downhill": 1,
    "Shaded Grove": 2,
    "Valley": 3,
    "Firefly Forest": 4,
    "Dahlia": 5,
    "Tunnels": 6,
    "Fields": 7,
    "Main Nexus": 8,
}


# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class DustforceLocation(Location):
    game = "Dustforce"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: DustforceWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: DustforceWorld) -> None:
    # Finally, we need to put the Locations ("checks") into their regions.
    # Once again, before we do anything, we can grab our regions we created by using world.get_region()
    main_nexus = world.get_region("Main Nexus")
    downhill = world.get_region("Downhill")
    shaded_grove = world.get_region("Shaded Grove")
    valley = world.get_region("Valley")
    firefly_forest = world.get_region("Firefly Forest")
    dahlia = world.get_region("Dahlia")
    tunnels = world.get_region("Tunnels")
    fields = world.get_region("Fields")

    # One way to create locations is by just creating them directly via their constructor.
    # # bottom_left_chest = DustforceLocation(
    # #     world.player, "Bottom Left Chest", world.location_name_to_id["Bottom Left Chest"], main_nexus
    # # )

    # You can then add them to the region.
    ##main_nexus.locations.append(bottom_left_chest)

    # A simpler way to do this is by using the region.add_locations helper.
    # For this, you need to have a dict of location names to their IDs (i.e. a subset of location_name_to_id)
    # Aha! So that's why we made that "get_location_names_with_ids" helper method earlier.
    # You also need to pass your overridden Location class.
    main_nexus_locations = get_location_names_with_ids(["Main Nexus"])
    main_nexus.add_locations(main_nexus_locations, DustforceLocation)

    downhill_locations = get_location_names_with_ids(["Downhill"])
    downhill.add_locations(downhill_locations, DustforceLocation)

    shaded_grove_locations = get_location_names_with_ids(["Shaded Grove"])  
    shaded_grove.add_locations(shaded_grove_locations, DustforceLocation)

    valley_locations = get_location_names_with_ids(["Valley"])
    valley.add_locations(valley_locations, DustforceLocation)

    firefly_forest_locations = get_location_names_with_ids(["Firefly Forest"])
    firefly_forest.add_locations(firefly_forest_locations, DustforceLocation)

    dahlia_locations = get_location_names_with_ids(["Dahlia"])
    dahlia.add_locations(dahlia_locations, DustforceLocation)

    tunnels_locations = get_location_names_with_ids(["Tunnels"])
    tunnels.add_locations(tunnels_locations, DustforceLocation)

    fields_locations = get_location_names_with_ids(["Fields"])
    fields.add_locations(fields_locations, DustforceLocation)

    # bottom_right_room_locations = get_location_names_with_ids(["Bottom Right Room Left Chest", "Bottom Right Room Right Chest"])
    # bottom_right_room.add_locations(bottom_right_room_locations, DustforceLocation)

    # top_left_room_locations = get_location_names_with_ids(["Top Left Room Chest"])
    # top_left_room.add_locations(top_left_room_locations, DustforceLocation)

    # right_room_locations = get_location_names_with_ids(["Right Room Enemy Drop"])
    # right_room.add_locations(right_room_locations, DustforceLocation)

    # Locations may be in different regions depending on the player's options.
    # In our case, the hammer option puts the Top Middle Chest into its own room called Top Middle Room.
    #TODO: Conditional location mappings
    # top_middle_room_locations = get_location_names_with_ids(["Top Middle Chest"])
    # if world.options.hammer:
    #     top_middle_room = world.get_region("Top Middle Room")
    #     top_middle_room.add_locations(top_middle_room_locations, DustforceLocation)
    # else:
    #     overworld.add_locations(top_middle_room_locations, DustforceLocation)

    # Locations may exist only if the player enables certain options.
    # In our case, the extra_starting_chest option adds the Bottom Left Extra Chest location.
    #TODO: Conditional locations
    # if world.options.extra_starting_chest:
    #     # Once again, it is important to stress that even though the Bottom Left Extra Chest location doesn't always
    #     # exist, it must still always be present in the world's location_name_to_id.
    #     # Whether the location actually exists in the seed is purely determined by whether we create and add it here.
    #     bottom_left_extra_chest = get_location_names_with_ids(["Bottom Left Extra Chest"])
    #     overworld.add_locations(bottom_left_extra_chest, DustforceLocation)


def create_events(world: DustforceWorld) -> None:
    print("Creating event locations (not implemented)")
    # Sometimes, the player may perform in-game actions that allow them to progress which are not related to Items.
    # In our case, the player must press a button in the top left room to open the final boss door.
    # AP has something for this purpose: "Event locations" and "Event items".
    # An event location is no different than a regular location, except it has the address "None".
    # It is treated during generation like any other location, but then it is discarded.
    # This location cannot be "sent" and its item cannot be "received", but the item can be used in logic rules.
    # Since we are creating more locations and adding them to regions, we need to grab those regions again first.
    # top_left_room = world.get_region("Top Left Room")
    # final_boss_room = world.get_region("Final Boss Room")

    # One way to create an event is simply to use one of the normal methods of creating a location.
    # button_in_top_left_room = DustforceLocation(world.player, "Top Left Room Button", None, top_left_room)
    # top_left_room.locations.append(button_in_top_left_room)

    # We then need to put an event item onto the location.
    # An event item is an item whose code is "None" (same as the event location's address),
    # and whose classification is "progression". Item creation will be discussed more in items.py.
    # Note: Usually, items are created in world.create_items(), which for us happens in items.py.
    # However, when the location of an item is known ahead of time (as is the case with an event location/item pair),
    # it is common practice to create the item when creating the location.
    # Since locations also have to be finalized after world.create_regions(), which runs before world.create_items(),
    # we'll create both the event location and the event item in our locations.py code.
    # button_item = items.DustforceItem("Top Left Room Button Pressed", ItemClassification.progression, None, world.player)
    # button_in_top_left_room.place_locked_item(button_item)

    # A way simpler way to do create an event location/item pair is by using the region.create_event helper.
    # Luckily, we have another event we want to create: The Victory event.
    # We will use this event to track whether the player can win the game.
    #TODO: add victory event?
    # The Victory event is a completely optional abstraction - This will be discussed more in set_rules().
    # final_boss_room.add_event(
    #     "Final Boss Defeated", "Victory", location_type=DustforceLocation, item_type=items.DustforceItem
    # )

    # If you create all your regions and locations line-by-line like this,
    # the length of your create_regions might get out of hand.
    # Many worlds use more data-driven approaches using dataclasses or NamedTuples.
    # However, it is worth understanding how the actual creation of regions and locations works,
    # That way, we're not just mindlessly copy-pasting! :)
