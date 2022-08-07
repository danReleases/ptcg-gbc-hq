from unidecode import unidecode
from slpp import slpp


def remove_non_ascii(text):
    sp_chars = {
        " ♀": "F",
        " ♂": "M",
    }
    for sp in sp_chars:
        if text.endswith(sp):
            text = text.replace(sp, sp_chars[sp])
    return unidecode(text)


def normalize_pokemon(name):
    name = "".join(
        [
            c
            for c in remove_non_ascii(name).upper()
            if c == " " or (ord(c) >= 65 and ord(c) <= 90)
        ]
    )
    name = name.replace(" ", "_")
    return name


def write_lua(dict_data: dict, fname: str) -> None:
    with open(fname, "w+") as f:
        f.write(f"return {slpp.encode(dict_data)}")
