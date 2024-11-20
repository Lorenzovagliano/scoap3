import requests
import json
import csv

def get_nested_field(json_obj, field_path):
    keys = field_path.split(".")
    results = []
    stack = [(json_obj, keys, keys[0])]

    while stack:
        current_obj, remaining_keys, current_path = stack.pop()

        if not remaining_keys:
            if current_obj is None:
                results.append((current_path, None))
            else:
                results.append((current_path, current_obj))
            continue

        key = remaining_keys[0]
        if isinstance(current_obj, list):
            for idx, item in enumerate(current_obj):
                stack.append((item, remaining_keys, f"{current_path}[{idx}]"))
        elif isinstance(current_obj, dict) and key in current_obj:
            stack.append((current_obj[key], remaining_keys[1:], f"{current_path}.{key}"))
        else:
            results.append((current_path + "." + key, None))

    return results


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

def analyze_fields(json_data, field_analysis):
    results = {}
    
    for field, analysis_type in field_analysis.items():
        result = get_nested_field(json_data, field)
        
        if analysis_type == "y/n":
            field_results = []
            for path, value in result:
                field_results.append(f"{path} = {'y' if value else 'n'}")
            results[field] = field_results
            
        elif analysis_type == "nr":
            arr = []
            for path, value in result:
                if value is not None:
                    arr.append(value)
            results[field] = f"{field} = nr: {len(arr)}"
            
        elif analysis_type == "data":
            field_results = [f"{path} = {value}" for path, value in result]
            results[field] = field_results
            
    return results


def write_to_json(dois, field_analysis, filename="output.json"):
    data = []
    
    for doi in dois:
        json_data = fetch_work_by_doi(doi)

        if json_data:
            analysis_results = analyze_fields(json_data, field_analysis)
            data.append({"doi": doi, "analysis": analysis_results})

    with open(filename, mode="w") as file:
        json.dump(data, file, indent=4)
    print(f"Data has been written to '{filename}'")


def write_to_csv(dois, field_analysis):
    all_fieldnames = set()

    all_rows = []

    for doi in dois:
        json_data = fetch_work_by_doi(doi)

        if json_data:
            analysis_results = analyze_fields(json_data, field_analysis)

            fieldnames = []
            contents = []

            for field, result in analysis_results.items():
                if isinstance(result, list):
                    for item in result:
                        fieldname = item.split(" = ")[0]
                        content = item.split(" = ")[1]
                        fieldnames.append(fieldname)
                        contents.append(content)
                        all_fieldnames.add(fieldname)
                else:
                    fieldname = result.split(" = ")[0]
                    content = result.split(" = ")[1]
                    fieldnames.append(fieldname)
                    contents.append(content)
                    all_fieldnames.add(fieldname)

            row = {'article': doi}
            for fieldname, content in zip(fieldnames, contents):
                row[fieldname] = content

            all_rows.append(row)

    sorted_fieldnames = ['article'] + sorted(all_fieldnames)

    with open('output.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=sorted_fieldnames)
        writer.writeheader()

        for row in all_rows:
            row_data = {fieldname: row.get(fieldname, "") for fieldname in sorted_fieldnames}
            writer.writerow(row_data)

    print("Data has been written to 'output.csv'")


def read_dois_from_csv(filename):
    dois = []
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            if 'doi' not in reader.fieldnames:
                raise ValueError("CSV file must contain a 'doi' column")
            for row in reader:
                if row['doi']:
                    dois.append(row['doi'])
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return dois


#Script Parameters:

field_analysis = {
    "accepted.date-parts": "y/n", 
    "author.given": "nr", 
    "author.family": "nr", 
    "author.sequence": "nr", 
    "author.ORCID": "nr", 
    "author.authenticated-orcid": "nr", 
    "DOI": "y/n", 
    "author.affiliation.name": "nr", 
    "author.affiliation.id.id": "nr", 
    "container-title": "y/n", 
    "ISSN": "y/n",
    "volume_year": "y/n", 
    "issue": "y/n", 
    "issue_date": "y/n", 
    "volume": "y/n", 
    "title": "y/n", 
    "article-number": "y/n", 
    "alternative-id": "y/n", 
    "relation.has-preprint.id": "y/n", 
    "relation.has-preprint.id-type": "y/n", 
    "author.affiliation.name": "y/n",
    "page": "data", 
    "abstract": "y/n", 
    "funder.award": "nr", 
    "funder.DOI": "nr", 
    "funder.name": "nr",
    "assertion.value": "data",
}

input_file = "dois.csv"
dois = read_dois_from_csv(input_file)

write_to_json(dois, field_analysis)
write_to_csv(dois, field_analysis)
