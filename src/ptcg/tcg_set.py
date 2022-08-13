import os
import requests
import json
from .tcg_card import TCGCard


class TCGSet:
    def __init__(self, api_key: str, set_id: str, set_data: dict = None) -> None:
        self.api = api_key
        self.headers = {"x-api-key": api_key}
        self.id = set_id
        self.data = set_data if set_data else {}
        self.cards = []
        if not self.data:
            self.update()
        self._load_cards()

    def _load_cards(self) -> None:
        self.cards = []
        for card in self.data:
            new_card = TCGCard(self.api, card["id"], card)
            self.cards.append(new_card)

    def update(self) -> None:
        data = []
        q = f"set.id:{self.id}"
        p = 1
        while True:
            request = f"https://api.pokemontcg.io/v2/cards?q={q}&page={p}"
            cards = requests.get(request, headers=self.headers).text
            r = json.loads(cards)
            if not r["data"]:
                break
            data.extend(r["data"])
            p += 1
        self.data = data

    def save_images(self, hi_res=True, re_fetch=False) -> None:
        dir = f"sets/images/{self.id}"
        fnames = {}
        for card in self.cards:
            fname = f"{dir}/{card.normalized_name}.png"
            fnames[card.normalized_name] = (fname, card.normalized_type)
            if not os.path.exists(fname) or re_fetch:
                card.save_image(fname)
        return fnames

    def save_json(self, fname):
        if not self.data:
            return
        with open(fname, "w+") as f:
            f.write(json.dumps(self.data))

    @classmethod
    def from_json(cls, api_key, fname):
        with open(fname, "r") as f:
            data = json.loads(f.read())
        set_id = data[0]["set"]["id"]
        return TCGSet(api_key, set_id, data)

    def __str__(self):
        return str(self.id)