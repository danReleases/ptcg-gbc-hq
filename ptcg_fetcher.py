# Fetch card images from https://pokemontcg.io
# Requires API key - export POKEMONTCG_IO_API_KEY='12345678-1234-1234-1234-123456789ABC'

import json
import requests
import os
import glob
from PIL import Image
from src.utils.helper import write_lua
from src.ptcg.tcg_set import TCGSet


class TCG:
    def __init__(
        self, api_key: str, ptcg_map: dict, regions: dict = None, cardsets: dict = None
    ):
        self.api = api_key
        self.headers = {"x-api-key": self.api}
        self.ptcg_map = ptcg_map
        self.regions = regions if regions else {}
        self.cardsets = cardsets if cardsets else {}  # limit api calls
        if not os.path.exists("sets"):
            os.makedirs("sets")
        elif not self.cardsets:
            set_files = glob.glob("sets/*.json")
            cardsets = [TCGSet.from_json(self.api, cardset) for cardset in set_files]
            for cardset in cardsets:
                self._add_set(cardset)

    def _add_set(self, cardset: TCGSet, save=False) -> None:
        if save:
            cardset.save_json(f"sets/{cardset.id}.json")
        self.cardsets[cardset.id] = cardset
        if not os.path.exists(f"sets/images/{cardset.id}"):
            os.makedirs(f"sets/images/{cardset.id}")
        if not os.path.exists(f"sets/images/{cardset.id}/processed"):
            os.makedirs(f"sets/images/{cardset.id}/processed")

    def _get_image_and_process(
        self, set_id: str, re_fetch=False, re_process=True, compress: int = 0
    ):
        cardset = self.cardsets.get(set_id)
        if not cardset:
            return
        areas = self.regions[set_id] if set_id in self.regions else None
        files_map = cardset.save_images(re_fetch=re_fetch)
        curr_dir_path = str(os.path.abspath(os.getcwd())).replace("\\", "//")    # set values to full path to avoid issues loading images in LUA
        dir = f"{curr_dir_path}/sets/images/{set_id}/processed"
        memory_map = {}
        for poke, values in files_map.items():
            fname = values[0]
            supertype = values[1]

            if poke not in self.ptcg_map:
                continue
            new_file = f"{dir}/{poke}.png"

            if not os.path.exists(new_file) or re_process:
                img = Image.open(fname)

                if areas:
                    region = areas[supertype]
                    region = (
                        region[0],
                        region[1],
                        region[0] + region[2],
                        region[1] + region[3],
                    )
                    img = img.crop(region)
                if compress > 0 and compress < 100:
                    img.save(new_file, "JPEG", quality=compress)
                else:
                    img.save(new_file)

            for mem in self.ptcg_map[poke]:
                memory_map[str(mem)] = new_file

        return memory_map

    def build_lua(
        self, cardset_ordered: list[str], fname, re_fetch=False, re_process=False
    ) -> str:
        mem_maps = []
        for cardset_id in cardset_ordered:
            mem_maps.append(
                self._get_image_and_process(cardset_id, re_fetch, re_process)
            )
        combined_dict = {k: v for d in mem_maps for k, v in d.items()}
        write_lua(combined_dict, fname)

    def _get_sets(self, set_name: str) -> list[str]:
        sets = requests.get(
            f"https://api.pokemontcg.io/v2/sets?q=name:{set_name}",
            headers=self.headers,
        )
        sets = sets.text
        return (
            [cardset["id"] for cardset in json.loads(sets)["data"]]
            if "data" in sets
            else []
        )

    def fetch(self, set_id: str) -> list[TCGSet]:
        if set_id in self.cardsets:
            return [self.cardsets[set_id]]
        new_cardsets = self._get_sets(set_name=set_id)
        found_sets = []
        for cardset_id in new_cardsets:
            cardset = (
                TCGSet(self.api, cardset_id)
                if cardset_id not in self.cardsets
                else self.cardsets[cardset_id]
            )
            found_sets.append(cardset)
            if not cardset_id in self.cardsets:
                self._add_set(found_sets[-1], save=True)
        return found_sets


if __name__ == "__main__":
    json_file_path = "regions.json"
    with open(json_file_path, "r") as j:
        img_regions = json.loads(j.read())

    from poketcg.tools.constants import cards
    from collections import defaultdict

    key = os.environ.get("POKEMONTCG_IO_API_KEY")

    cards = {v: k for k, v in cards.items()}
    cards_base = defaultdict(list)
    for k, v in cards.items():
        if k[-1] in ("1", "2", "3"):
            k = k[:-1]
        cards_base[k].extend([v])

    tcg = TCG(key, cards_base, img_regions)
    sets_in_order = []
    sets_in_order.extend(list(map(str, tcg.fetch("base")))[::-1])
    sets_in_order.extend(list(map(str, tcg.fetch("hgss1"))))
    tcg.build_lua(sets_in_order, "lua/sets/custom.lua")
