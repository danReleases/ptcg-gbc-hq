import os
import requests
import json
from ..utils.helper import normalize_pokemon, remove_non_ascii


class TCGCard:
    def __init__(self, api_key: str, card_id: str, card_dict: dict = None) -> None:
        self.headers = {"x-api-key": api_key}
        self.id = card_id
        self.data = card_dict if card_dict else {}
        if not self.data:
            self.update()
        self._normalize()

    def _normalize(self) -> None:
        self.normalized_name = normalize_pokemon(self.data["name"])
        self.normalized_type = remove_non_ascii(self.data["supertype"])

    def update(self) -> None:
        card = requests.get(
            f"https://api.pokemontcg.io/v2/cards/{self.id}", headers=self.headers
        )
        self.data = json.loads(card)
        self._normalize()

    def save_image(self, fname: str, hi_res=True) -> None:
        card = self.data
        res = "large" if hi_res else "small"
        url = card["images"][res]
        img = requests.get(url).content
        with open(fname, "wb+") as f:
            f.write(img)
    
    def __str__(self):
        return str(self.normalized_name)