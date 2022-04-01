import requests


def build_graph_sharepoint_list_url(site_id, list_id):
    graph_root_url = "https://graph.microsoft.com/v1.0"
    return "/".join([graph_root_url, "sites", site_id, "lists", list_id, "items"])

def fetch_sharepoint_list_items(token, list_url, querystring=None, fields=None, headers=dict(), return_json=True):
    if querystring is not None:
        url += f"?{querystring}"
    
    headers =headers["Authorization"] = f"Bearer {token['access_token']}"
    list_items = requests.get(url, headers=headers)

    if return_json:
        list_items = list_items.json()
    
    return list_items



