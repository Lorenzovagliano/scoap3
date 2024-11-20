import requests

def fetch_works(output_file, journal_name=None, publisher_name=None, from_pub_date=None, to_pub_date=None):
    base_url = "https://api.crossref.org/works"
    
    filters = []
    if from_pub_date:
        filters.append(f"from-pub-date:{from_pub_date}")
    if to_pub_date:
        filters.append(f"until-pub-date:{to_pub_date}")
    
    if journal_name:
        query_params = {"query.container-title": journal_name}
    elif publisher_name:
        query_params = {"query.publisher-name": publisher_name}
    else:
        raise ValueError("Either a journal name or a publisher name must be provided.")
    
    if filters:
        query_params["filter"] = ",".join(filters)
    
    try:
        response = requests.get(base_url, params=query_params)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("message", {}).get("items", [])
        dois = [item.get("DOI") for item in items if "DOI" in item]
        
        with open(output_file, 'w') as file:
            for doi in dois:
                file.write(doi + '\n')
        
        print(f"DOIs have been written to {output_file}")
        
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

fetch_works("dois.txt", journal_name="APS", from_pub_date="2024-01-01", to_pub_date="2024-01-01")
