import json
import os

def normalize():
    data_path = "/Users/erictomlinson/projects/SpotBotRoot/SpotBotData/SpotBotData/finalCombinedExercises.json"
    map_path = "/Users/erictomlinson/projects/SpotBotRoot/SpotBotData/Scripts/normalization_map.json"
    output_path = "/Users/erictomlinson/projects/SpotBotRoot/SpotBotData/SpotBotData/normalizedExercises.json"

    if not os.path.exists(data_path):
        print(f"Error: Data path {data_path} does not exist.")
        return

    with open(data_path, 'r') as f:
        exercises = json.load(f)
    
    with open(map_path, 'r') as f:
        norm_map = json.load(f)

    normalized_data = {}

    for ex in exercises:
        # Standardize Name for Deduplication
        raw_name = ex.get("name", "unknown").lower().strip()
        
        # Determine unique key (normalized name)
        key = raw_name

        if key not in normalized_data:
            normalized_data[key] = {
                "name": ex.get("name"),
                "equipment": None,
                "primaryMuscles": [],
                "secondaryMuscles": [],
                "instructions": [],
                "images": [],
                "category": ex.get("category"),
                "difficulty": ex.get("difficulty") or ex.get("level")
            }

        entry = normalized_data[key]

        # 1. Normalize Equipment
        eq = ex.get("equipment")
        if eq is not None:
            eq = norm_map["equipment"].get(str(eq).lower(), eq)
        if not entry["equipment"]:
            entry["equipment"] = eq

        # 2. Normalize Muscles (Merge Schema 1 & 2)
        muscles = set(entry["primaryMuscles"])
        if "primaryMuscles" in ex:
            for m in ex["primaryMuscles"]:
                muscles.add(norm_map["muscles"].get(m.lower(), m.lower()))
        if "target" in ex:
            m = ex["target"]
            muscles.add(norm_map["muscles"].get(m.lower(), m.lower()))
        entry["primaryMuscles"] = list(muscles)

        # 3. Merge Instructions (Prefer longer/more detailed)
        new_instr = ex.get("instructions", [])
        if isinstance(new_instr, str):
            new_instr = [new_instr]
        
        if len(new_instr) > len(entry["instructions"]):
            entry["instructions"] = new_instr

        # 4. Merge Images
        new_imgs = ex.get("images", [])
        if new_imgs and not entry["images"]:
            entry["images"] = new_imgs

    # Convert back to list
    final_list = list(normalized_data.values())

    with open(output_path, 'w') as f:
        json.dump(final_list, f, indent=2)
    
    print(f"Normalized {len(final_list)} unique exercises. Saved to {output_path}")

if __name__ == "__main__":
    normalize()
