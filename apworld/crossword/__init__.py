import base64
import dataclasses
from enum import Enum
import math
import random
from typing import Optional
import zlib

from BaseClasses import Item, ItemClassification, Region, Tutorial

from worlds.AutoWorld import WebWorld, World
from worlds.crossword.Types import Clue, CrossLetter, ParsedPuz, SlotData

from .Items import CrosswordItem, item_table
from .Locations import MAX_N_CLUES, CrosswordLocation, get_location_id, location_table, get_location_name

from .Options import CrosswordOptions
from .puz_parser import parse_puz, parse_grid_layout

class CrosswordWeb(WebWorld):
    tutorials = [
        # Tutorial(
        #     "Multiworld Setup Guide",
        #     "A guide to setting up Crossword. This guide covers single-player, multiworld, and website.",
        #     "English",
        #     "setup_en.md",
        #     "setup/en",
        #     ["jm771"],
        # )
    ]

def get_vibes(hope, madness):
    sub_vibes = [6, 12, 3, 81, 23]
    product = 1
    for vibe in sub_vibes:
        product *= vibe
    return int(f"{math.pow(product, 1/len(sub_vibes)):.0f}") * (-1) ** madness

def parse_puz_for_rando(data: bytes) -> ParsedPuz:
    clue_map, letter_list = parse_puz(data)
    cross_letters = [CrossLetter(clueid, index, letter) for letter, locs in letter_list for clueid, index in locs]
    clues = [Clue(clueid.direction, clueid.number, clueinfo.clue, clueinfo.answer) for clueid, clueinfo in clue_map.items()]
    return ParsedPuz(clues, cross_letters)

def get_perc(a, b):
    return (a * b + 99) // 100

class CrosswordWorld(World):
    """
    Solve a Crossword puzzle!
    """

    game: str = "Crossword"
    options_dataclass = CrosswordOptions

    web = CrosswordWeb()

    item_name_to_id = {name: data.code for name, data in item_table.items()}

    location_name_to_id = location_table

    ap_world_version = "0.0.0"

    parsed_crossword: Optional[ParsedPuz]

    def generate_early(self):
        options: CrosswordOptions = self.options
        if (bool(options.puz_file_path.value) == bool(options.puz_file_contents.value)):
            raise Exception("must provide exactly one of puz_file_path or puz_file_contents")

        if options.puz_file_path.value:                
            with open(options.puz_file_path.value, "rb") as f:
                data = f.read()
        else:
            compressed_data = base64.b64decode(options.puz_file_contents.value)
            data = zlib.decompress(compressed_data)


        self.puz_data = data
        self.parsed_crossword = parse_puz_for_rando(data)
        if options.cross_letter_generation.value == 1:
            all_cross_letters = [CrossLetter(clue.get_id(), i, letter) 
                                 for clue in self.parsed_crossword.clues
                                 for i, letter in enumerate(clue.answer)]
            self.parsed_crossword = dataclasses.replace(self.parsed_crossword, cross_letters=all_cross_letters)

        self.random.shuffle(self.parsed_crossword.clues)
        self.random.shuffle(self.parsed_crossword.cross_letters)

    def create_regions(self):        
        menu = Region("Menu", self.player, self.multiworld)

        # n_clues = len(self.parsed_crossword.clues)
    
        menu.locations = [CrosswordLocation(self.player, get_location_name(c.number, c.direction), get_location_id(c.number, c.direction), menu) for c in self.parsed_crossword.clues]
        n_starting = self.get_n_starting()

        n_clue_rewards, _ = self.get_reward_split()

        for i, loc in enumerate(menu.locations):
            if len(menu.locations) > n_starting:
                n_items_required = math.ceil((i - n_starting + 1) * n_clue_rewards / (len(menu.locations) - n_starting))
            else:
                n_items_required = 0
            loc.access_rule = lambda state, nitems=n_items_required: state.has("Clue Unlock", self.player, nitems) if n_items_required > 0 else lambda state: True
        
        # Change the victory location to an event and place the Victory item there.
        victory_location = CrosswordLocation(self.player, "VictoryLocation", None, menu)
        victory_location.place_locked_item(Item("Victory", ItemClassification.progression, None, self.player))
        victory_location.access_rule = lambda state, nitems=n_items_required: state.has("Clue Unlock", self.player, nitems)
        menu.locations += [victory_location]        
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        self.multiworld.regions += [menu]

    def get_reward_split(self):
        n_locations_for_items = len(self.parsed_crossword.clues)
        # Need to be able to put something other than clue unlock at victory location
        n_clue_locations = min(n_locations_for_items-1, max(1, get_perc(n_locations_for_items, self.options.clue_item_fraction.value)))
        n_cross_letter_locations = n_locations_for_items - n_clue_locations

        return n_clue_locations, n_cross_letter_locations

    def create_items(self):
        hope = 1
        vibes = get_vibes(hope, 7)
        
        n_clue_locations, n_cross_letter_locations = self.get_reward_split()

        self.multiworld.itempool += [self.create_item("Clue Unlock") for i in range (0 + vibes, n_clue_locations + vibes)]
        self.multiworld.itempool += [self.create_item("Cross Letter") for i in range (0, n_cross_letter_locations)]



    def create_item(self, name: str) -> Item:
        item_data = item_table[name]
        item = CrosswordItem(name, item_data.classification, item_data.code, self.player)
        return item


    def fill_slot_data(self):
        options: CrosswordOptions = self.options
        n_clue_locations, n_cross_letter_locations = self.get_reward_split()
        n_clue_unlocks = get_perc(len(self.parsed_crossword.clues), options.clue_alloc_percent.value) - self.get_n_starting()
        n_cross_letter_unlocks = get_perc(len(self.parsed_crossword.cross_letters), options.cross_letter_alloc_percent.value)

        clues_per_reward = (n_clue_unlocks / n_clue_locations) + 0.01
        cross_letters_per_reward = (n_cross_letter_unlocks / n_cross_letter_locations) + 0.01 if options.clue_item_fraction < 100 else 0

        slot_dataclass = SlotData(self.get_n_starting(), clues_per_reward, cross_letters_per_reward, self.parsed_crossword.clues, self.parsed_crossword.cross_letters)

        def dictfactory(data):
            return { k: v.value if isinstance(v, Enum) else v for k, v in data}

        slot_data = dataclasses.asdict(slot_dataclass, dict_factory=dictfactory)
        # Grid shape so web clients can draw the real puzzle (extra key, older clients ignore it)
        slot_data["grid"] = parse_grid_layout(self.puz_data)
        return slot_data
    
    def get_n_starting(self):
        return max(1, get_perc(self.options.starting_percent.value, len(self.parsed_crossword.clues)))
    # def open_page(url):
    #     import webbrowser
    #     import re
    #     # Extract slot, pass, host, and port from the URL
    #     # URL format: archipelago://slot:pass@host:port
    #     match = re.match(r"archipelago://([^:]+):([^@]+)@([^:]+):(\d+)", url)
    #     if not match:
    #         raise ValueError("Invalid URL format")
        
    #     slot, password, host, port = match.groups()
    #     if password == "None":
    #         webbrowser.open(f"http://Crossword-ap.netlify.app/?hostport={host}:{port}&name={slot}")
    #     else:
    #         webbrowser.open(f"http://Crossword-ap.netlify.app/?hostport={host}:{port}&name={slot}&password={password}")

    # components.append(
    #     Component(
    #         "Crossword AutoLaunch",
    #         func=open_page,
    #         component_type=component_type.HIDDEN,
    #         supports_uri=True,
    #         game_name="Crossword"
    #     )
    # )