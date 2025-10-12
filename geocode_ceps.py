import json
import time
from pathlib import Path

import requests


def cep_to_coords_viacep(
    ceps: list[str], output_path="data/cep_coords_viacep.json"
) -> None:
    """Geocode CEP using ViaCEP + Nominatim. Saves to file."""

    # Load cache from same file
    cache = {}
    if Path(output_path).exists():
        with open(output_path) as f:
            cache = json.load(f)

    def cep_to_coords_viacep_single(cep):
        """Geocode CEP using ViaCEP + Nominatim"""
        # Check cache first
        if cep in cache:
            return cache[cep]

        cep_clean = cep.replace("-", "")
        via_url = f"https://viacep.com.br/ws/{cep_clean}/json/"
        addr = requests.get(via_url).json()

        if "erro" in addr:
            result = (None, None)
        else:
            query = f"{addr.get('logradouro', '')}, {addr.get('localidade', '')}, DF, Brazil"
            nom_url = "https://nominatim.openstreetmap.org/search"

            # Comply: User-Agent + 1 req/sec
            time.sleep(1.1)  # Rate limit
            geo = requests.get(
                nom_url,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "gustavo@arcos.org.br"},
            ).json()

            result = (
                (float(geo[0]["lat"]), float(geo[0]["lon"])) if geo else (None, None)
            )

        # Cache result
        cache[cep] = result
        with open(output_path, "w") as f:
            json.dump(cache, f)

        return result

    # Get coordinates for each CEP
    coords_dict = {}
    for cep in ceps:
        try:
            lat, lon = cep_to_coords_viacep_single(cep)
            coords_dict[cep] = (lat, lon)
        except Exception as e:
            print(f"Error processing CEP {cep}: {e}")
            coords_dict[cep] = (None, None)


def cep_to_coords_ipedf(
    ceps: list[str],
    output_path="data/cep_coords.json",
) -> None:
    """Geocode CEP using DF government's API. Saves to file."""

    # Load cache from same file
    cache = {}
    if Path(output_path).exists():
        with open(output_path) as f:
            cache = json.load(f)

    def cep_to_coords_ipedf_single(cep):
        """Geocode CEP directly using DF government's API"""
        # Check cache first
        if cep in cache:
            return cache[cep]

        try:
            url = "https://geocode.ipe.df.gov.br/api/"
            params = {"localidade": cep, "limite": 1}

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                result = (coords[1], coords[0])  # lat, lon (GeoJSON is lon, lat)
            else:
                result = (None, None)

            # Cache the result
            cache[cep] = result
            with open(output_path, "w") as f:
                json.dump(cache, f)

            return result

        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates for CEP {cep}: {e}")
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing response for CEP {cep}: {e}")
        except Exception as e:
            print(f"Unexpected error for CEP {cep}: {e}")

        result = (None, None)
        # Cache the failed result too
        cache[cep] = result
        with open(output_path, "w") as f:
            json.dump(cache, f)
        return result

    # Get coordinates for each CEP
    coords_dict = {}
    for cep in ceps:
        try:
            lat, lon = cep_to_coords_ipedf_single(cep)
            coords_dict[cep] = (lat, lon)
        except Exception as e:
            print(f"Error processing CEP {cep}: {e}")
            coords_dict[cep] = (None, None)


# if __name__ == "__main__":
#     ceps = ["70297400", "70000000", "70800120"]
#     cep_to_coords_ipedf(ceps, "test_cep_ipedf.json")
#     cep_to_coords_viacep(ceps, "test_cep_viacep.json")
