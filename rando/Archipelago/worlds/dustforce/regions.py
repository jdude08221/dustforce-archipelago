from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import DustforceWorld

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).


def create_and_connect_regions(world: DustforceWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: DustforceWorld) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    main_nexus = Region("Main Nexus", world.player, world.multiworld)
    downhill = Region("Downhill", world.player, world.multiworld)
    shaded_grove = Region("Shaded Grove", world.player, world.multiworld)
    valley = Region("Valley", world.player, world.multiworld)
    firefly_forest = Region("Firefly Forest", world.player, world.multiworld)
    dahlia = Region("Dahlia", world.player, world.multiworld)
    tunnels = Region("Tunnels", world.player, world.multiworld)
    fields = Region("Fields", world.player, world.multiworld)

    # Let's put all these regions in a list.
    regions = [main_nexus, downhill, shaded_grove, valley, firefly_forest, dahlia, tunnels, fields]

    # Some regions may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    #TODO: Conditional regions, possibly difficults not sure
    # if world.options.hammer:
    #     top_middle_room = Region("Top Middle Room", world.player, world.multiworld)
    #     regions.append(top_middle_room)

    # We now need to add these regions to multiworld.regions so that AP knows about their existence.
    world.multiworld.regions += regions


def connect_regions(world: DustforceWorld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).
    main_nexus = world.get_region("Main Nexus")
    downhill = world.get_region("Downhill")
    shaded_grove = world.get_region("Shaded Grove")
    valley = world.get_region("Valley")
    firefly_forest = world.get_region("Firefly Forest")
    dahlia = world.get_region("Dahlia")
    tunnels = world.get_region("Tunnels")
    fields = world.get_region("Fields")

    main_nexus.connect(downhill, "Main Nexus to Downhill")
    main_nexus.connect(shaded_grove, "Main Nexus to Shaded Grove")
    main_nexus.connect(valley, "Main Nexus to Valley")
    main_nexus.connect(firefly_forest, "Main Nexus to Firefly Forest")
    main_nexus.connect(dahlia, "Main Nexus to Dahlia")
    main_nexus.connect(tunnels, "Main Nexus to Tunnels")
    main_nexus.connect(fields, "Main Nexus to Fields")


    # The region.connect helper even allows adding a rule immediately.
    # We'll talk more about rule creation in the set_all_rules() function in rules.py.
    #main_nexus.connect(top_left_room, "Main Nexus to Top Left Room", lambda state: state.has("Key", world.player))

    # Some Entrances may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.

    #TODO add conditional connections depending on options
    # if world.options.hammer:
    #     top_middle_room = world.get_region("Top Middle Room")
    #     main_nexus.connect(top_middle_room, "Main Nexus to Top Middle Room")
