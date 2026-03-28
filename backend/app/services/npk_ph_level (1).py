import csv
import difflib
import re 


class SoilDataLookup:
    def __init__(self, csv_file):
        self.data = {}
        self._load_data(csv_file)

        # 🔥 Alias mapping
        self.aliases = {
            "hp": "himachal pradesh",
            "ap": "andhra pradesh",
            "cg": "chhattisgarh",
            "andaman": "andaman & nicobar",
        }

    def _load_data(self, csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                state = row["State"].strip().lower()

                self.data[state] = {
                    "N": float(row["Nitrogen (N)"]),
                    "P": float(row["Phosphorous (P)"]),
                    "K": float(row["Potassium (K)"]),
                    "pH": self.convert_ph_to_numeric(row["Predominant pH"])
                }

    def convert_ph_to_numeric(self , text):
        if not text:
            return None

        # extract percentage
        match = re.search(r"([\d.]+)%", text)
        percent = float(match.group(1)) if match else 100

        text_lower = text.lower()

        # base mapping
        if "acidic" in text_lower:
            base = 3
        elif "alkaline" in text_lower:
            base = 9
        else:
            base = 7  # neutral

        # normalize adjustment (0–100 → small shift)
        adjustment = (percent / 100) * 2  # max ±2 range shift

        # final pH score
        return round(base + adjustment - 1, 2)
        
    def get_npk_ph(self, state_name):
        state_name = state_name.strip().lower()

        # 1. Direct match
        if state_name in self.data:
            return self.data[state_name]

        # 2. Alias match
        if state_name in self.aliases:
            return self.data.get(self.aliases[state_name], "State not found")

        # 3. Partial match
        for state in self.data:
            if state_name in state:
                return self.data[state]

        # 4. Fuzzy match
        matches = difflib.get_close_matches(state_name, self.data.keys(), n=1, cutoff=0.6)
        if matches:
            return self.data[matches[0]]

        return "State not found"


if __name__ == "__main__":
    from pathlib import Path
    lookup_npk_path = str(Path(__file__).resolve().parent.parent/ "data"/"soil_state_data.csv")
    print(SoilDataLookup(lookup_npk_path).get_npk_ph("orissa"))