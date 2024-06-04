import httpx


async def fetch_search_results(base_link, folder_id, api_key, query):
    url = f"{base_link}?folderid={folder_id}&apikey={api_key}&query={query}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
