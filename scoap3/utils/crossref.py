import requests
import json
import csv

def fetch_work_by_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {})
    except requests.RequestException as e:
        print(f"An error occurred for DOI {doi}: {e}")
        return None

def flatten_json(json_obj, parent_key='', sep='.'):
    items = {}
    for key, value in json_obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, sep=sep))
        
        elif isinstance(value, list):
            # Special case for 'author' and 'reference' lists
            if key == "author" and value:
                for idx in range(min(2, len(value))):
                    items.update(flatten_json(value[idx], f"{new_key}[{idx}]", sep=sep))
            elif key == "reference" and value:
                for idx in range(min(1, len(value))):
                    items.update(flatten_json(value[idx], f"{new_key}[{idx}]", sep=sep))
            elif key == "funder" and value:
                for idx in range(min(1, len(value))): 
                    items.update(flatten_json(value[idx], f"{new_key}[{idx}]", sep=sep))
            else:
                if all(isinstance(i, dict) for i in value):
                    for idx, item in enumerate(value):
                        items.update(flatten_json(item, f"{new_key}[{idx}]", sep=sep))
                else:
                    items[new_key] = json.dumps(value)
        
        else:
            items[new_key] = value
    
    return items

def fetch_works_from_json(records):
    all_keys = set()
    results = []
    
    for record in records:
        doi = record[0]
        print(f"Fetching work for DOI: {doi}")
        metadata = fetch_work_by_doi(doi)
        
        if metadata:
            flattened_metadata = flatten_json(metadata)
            results.append(flattened_metadata)
            all_keys.update(flattened_metadata.keys())
    
    return results, all_keys

def write_metadata_to_csv(metadata_list, all_keys, output_file):
    if not metadata_list:
        print("No metadata to write.")
        return
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=sorted(all_keys))
        
        writer.writeheader()
        
        for metadata in metadata_list:
            writer.writerow(metadata)

    print(f"Metadata successfully written to {output_file}")

records = [
    ['10.1103/PhysRevD.110.102006'],
]

metadata_list, all_keys = fetch_works_from_json(records)

write_metadata_to_csv(metadata_list, all_keys, "output_metadata_flattened.csv")
