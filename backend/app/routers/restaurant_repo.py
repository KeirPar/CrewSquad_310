from pathlib import Path
import json, os
from typing import List, Dict, Any
#took this from the example code we were give, not sure if this will work for us. May have to change later...

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurant.json"

def load_all() -> List[Dict[str, Any]]:
   if not DATA_PATH.exists():
       return []
   with DATA_PATH.open("r", encoding="utf-8") as f:
       return json.load(f)

def save_all(items: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
