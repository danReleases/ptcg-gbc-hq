# Fetch card images from https://pokemontcg.io
# Requires API key - export POKEMONTCG_IO_API_KEY='12345678-1234-1234-1234-123456789ABC'

import json
import requests
import os
import logging
import glob
from PIL import Image
from slpp import slpp
from unidecode import unidecode


class TCG:
    def __init__(
        self, api_key: str, ptcg_map: dict, img_regions: dict = None, sets: dict = None
    ):
        self.key_headers = {"x-api-key": api_key}
        self.ptcg_map = ptcg_map
        self.img_regions = img_regions
        self.sets = sets if sets else {}  # limit api calls
        if not os.path.exists("sets"):
            os.makedirs("sets")
        elif not self.sets:
            sets = glob.glob("sets/*.json")
            sets = {st.split("\\")[-1].split(".")[0]: st for st in sets}
            self.sets = sets

    @classmethod
    def remove_non_ascii(cls, text):
        sp_chars = {
            " ♀": "F",
            " ♂": "M",
        }
        for sp in sp_chars:
            if text.endswith(sp):
                text = text.replace(sp, sp_chars[sp])
        return unidecode(text)

    @classmethod
    def _make_lua_map(cls, set_id, file_map):
        with open(f"lua/sets/{set_id}.lua", "w+") as f:
            f.write(f"return {slpp.encode(file_map)}")
        return True

    def _process_images(self, set_id, crop=True, quality=0):
        files = glob.glob(f"sets/images/{set_id}/*.png")
        for f in files:
            supertype = f.split("_")[-1].split(".")[0]
            img = Image.open(f)
            if crop and set_id in self.img_regions:
                region = self.img_regions[set_id][supertype]
                region = (
                    region[0],
                    region[1],
                    region[0] + region[2],
                    region[1] + region[3],
                )
                img = img.crop(region)
            if quality > 0:
                img.save(f, "JPEG", quality=quality)
            else:
                img.save(f)

    def _map(self, set_id: str):
        remaining_map = list(self.ptcg_map.values())
        file_map = {}
        files = glob.glob(f"sets/images/{set_id}/*.png")
        for f in files:
            fname = f.split("\\")[-1]
            fname = fname.split("_", 1)[-1] if fname.count("_") > 1 else fname
            pokemon = fname.split("_")[0].replace(" ", "_")
            if pokemon in self.ptcg_map:
                pk = self.ptcg_map[pokemon]
                mem_value = str(pk)
                fname = f"{mem_value}_{fname}"
                fname = "\\".join([*(f.split("\\")[:-1]), "\\\\", fname])
                os.replace(f, fname)
                # update dict
                file_map[mem_value] = fname
                if pk in remaining_map:
                    remaining_map.remove(pk)  # TODO: de-map before save new images

        if remaining_map:
            logging.error(f"{set_id}: Unable to map: {remaining_map}.")
        return file_map

    def save_images(
        self, set_id: str, start=None, end=None, get_hi_res=True, compress=0
    ):
        if not set_id in self.sets:
            return False
        dir = f"sets/images/{set_id}"
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(self.sets[set_id], "r") as f:
            set_data = json.loads(f.read())

        start = 0 if start is None else start
        end = len(set_data) if end is None else end

        for card in set_data[start:end]:
            card["supertype"] = TCG.remove_non_ascii(card["supertype"])
            card["name"] = "".join(
                [
                    c
                    for c in TCG.remove_non_ascii(card["name"]).upper()
                    if c == " " or (ord(c) >= 65 and ord(c) <= 90)
                ]
            )

            res = "large" if get_hi_res else "small"
            url = card["images"][res]
            img = requests.get(url).content

            img_file = f"{dir}/{card['name']}_{card['supertype']}.png"
            with open(img_file, "wb+") as f:
                f.write(img)
        if compress > 0 or set_id in self.img_regions:
            self._process_images(set_id, True, compress)
        return TCG._make_lua_map(set_id, self._map(set_id))

    def get(self, set_name: str, update=False):
        new_sets = (
            [st["id"] for st in self.get_sets(set_name)["data"]]
            if not set_name in self.sets
            else [set_name]
        )
        data = {}
        for st in new_sets:
            if not st in self.sets or update:
                cards = self.cards_by_set(st)
                if not cards:
                    continue
                self.sets[st] = f"sets/{st}.json"
                with open(self.sets[st], "w+") as f:
                    f.write(json.dumps(cards))
                logging.error(
                    f"New set created: {st}. You can use the new id to get data."
                )
            with open(self.sets[st], "r") as f:
                data[st] = json.loads(f.read())
        return data

    def get_sets(self, set_name: str):
        sets = requests.get(
            f"https://api.pokemontcg.io/v2/sets?q=name:{set_name}",
            headers=self.key_headers,
        )
        sets = sets.text
        return json.loads(sets)

    def cards_by_set(self, set_id: str):
        data = []
        q = f"set.id:{set_id}"
        p = 1
        while True:
            request = f"https://api.pokemontcg.io/v2/cards?q={q}&page={p}"
            cards = requests.get(request, headers=self.key_headers).text
            r = json.loads(cards)
            if not r["data"]:
                break
            data.extend(r["data"])
            p += 1
        return data


if __name__ == "__main__":
    json_file_path = "regions.json"
    with open(json_file_path, "r") as j:
        img_regions = json.loads(j.read())

    from poketcg.tools.constants import cards

    cards = {v: k for k, v in cards.items()}
    cards_base = {}
    for k, v in cards.items():
        if k[-1] in ("1", "2", "3"):
            if k[-1] == "1":
                k = k[:-1]
            else:
                continue
        cards_base[k] = v

    API_KEY = os.environ.get("POKEMONTCG_IO_API_KEY")

    tcg = TCG(API_KEY, cards_base, img_regions)

    bases = tcg.get("base")
    for b in bases:
        tcg.save_images(b)
