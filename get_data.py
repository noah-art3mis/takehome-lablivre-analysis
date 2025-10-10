import json
import time

import requests


def get_data(page: int) -> dict:
    url = "https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento"
    params = {"uf": "DF", "pagina": page, "tamanhoDaPagina": 100}
    headers = {"accept": "*/*"}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get data: {response.status_code}")

    return response.json()


def main():
    # inelegant but expedient. surely they dont have 10000 items
    for page in range(100):
        response = get_data(page)
        print(f"Page {page} processed")

        # save raw data first so if there are issues, we don't depend on the api
        with open(f"data/data-{page}.json", "w", encoding="utf-8") as f:
            json.dump(response["content"], f, indent=4)
        print(f"Data saved to data/data-{page}.json")

        time.sleep(1)

        page += 1


if __name__ == "__main__":
    main()
