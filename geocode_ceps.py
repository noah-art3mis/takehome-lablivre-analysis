"""
Módulo para geocodificação de CEPs usando APIs gratuitas.

Usa:
- ViaCEP: Para obter endereço do CEP
- Nominatim (OpenStreetMap): Para converter endereços em coordenadas
"""

import json
import os
import re
import time
from typing import Optional, Tuple

import pandas as pd
import requests


def clean_cep(cep: str) -> Optional[str]:
    """
    Limpa e valida um CEP.

    Args:
        cep: CEP em qualquer formato

    Returns:
        CEP com 8 dígitos ou None se inválido
    """
    if pd.isna(cep):
        return None
    cep = str(cep).strip()
    # Remover caracteres não numéricos
    cep = re.sub(r"[^0-9]", "", cep)
    # CEP válido tem 8 dígitos
    if len(cep) == 8:
        return cep
    return None


def geocode_cep(cep: str) -> Optional[Tuple[float, float, str]]:
    """
    Geocodifica um CEP usando ViaCEP + Nominatim.

    Args:
        cep: CEP com 8 dígitos (apenas números)

    Returns:
        Tupla (latitude, longitude, localidade) ou None se falhar

    Note:
        Inclui rate limiting de 1 segundo para respeitar limites da API Nominatim.
    """
    if not cep:
        return None

    try:
        # ViaCEP API
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Se o CEP não existe ou tem erro
            if "erro" in data:
                return None

            # ViaCEP não retorna coordenadas, então usamos Nominatim para geocoding
            endereco_completo = f"{data.get('logradouro', '')}, {data.get('bairro', '')}, {data.get('localidade', '')}, {data.get('uf', '')}, Brazil"

            # Nominatim (OpenStreetMap) - free geocoding
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {"q": endereco_completo, "format": "json", "limit": 1}
            headers = {
                "User-Agent": "LabLivre-Analysis/1.0"  # Nominatim requer User-Agent
            }

            time.sleep(1)  # Rate limiting - Nominatim requer 1 segundo entre requests

            geo_response = requests.get(
                nominatim_url, params=params, headers=headers, timeout=10
            )

            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                if geo_data:
                    lat = float(geo_data[0]["lat"])
                    lon = float(geo_data[0]["lon"])
                    localidade = data.get("localidade", "Unknown")
                    return (lat, lon, localidade)

        return None

    except Exception as e:
        print(f"Erro ao geocodificar CEP {cep}: {e}")
        return None


def load_cache(cache_file: str = "results/cep_geocode_cache.json") -> dict:
    """
    Carrega cache de coordenadas do arquivo JSON.

    Args:
        cache_file: Caminho do arquivo de cache

    Returns:
        Dicionário com CEPs e coordenadas
    """
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict, cache_file: str = "results/cep_geocode_cache.json") -> None:
    """
    Salva cache de coordenadas em arquivo JSON.

    Args:
        cache: Dicionário com CEPs e coordenadas
        cache_file: Caminho do arquivo de cache
    """
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)


def geocode_dataframe(
    df: pd.DataFrame,
    cep_column: str = "cep",
    cache_file: str = "results/cep_geocode_cache.json",
    limit: Optional[int] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Adiciona colunas de coordenadas a um DataFrame baseado nos CEPs.

    Args:
        df: DataFrame com coluna de CEPs
        cep_column: Nome da coluna de CEP
        cache_file: Caminho do arquivo de cache
        limit: Número máximo de CEPs únicos para geocodificar (None = todos)
        verbose: Se True, mostra progresso

    Returns:
        DataFrame com colunas adicionais: cep_clean, latitude, longitude, localidade
    """
    df = df.copy()

    # Limpar CEPs
    df["cep_clean"] = df[cep_column].apply(clean_cep)

    if verbose:
        print(f"CEPs válidos: {df['cep_clean'].notna().sum()}")
        print(f"CEPs únicos: {df['cep_clean'].nunique()}")

    # Carregar cache
    cache = load_cache(cache_file)
    if verbose and cache:
        print(f"Cache carregado: {len(cache)} CEPs")

    # Geocodificar CEPs únicos
    unique_ceps = df[df["cep_clean"].notna()]["cep_clean"].unique()

    if limit:
        unique_ceps = unique_ceps[:limit]
        if verbose:
            print(f"Limitando a {limit} CEPs únicos")

    if verbose:
        print(f"Geocodificando {len(unique_ceps)} CEPs únicos...")
        print(f"Tempo estimado: ~{len(unique_ceps)} segundos")

    # Geocodificar
    for i, cep in enumerate(unique_ceps):
        if cep not in cache:
            result = geocode_cep(cep)
            cache[cep] = result

            if verbose:
                status = "✓" if result else "✗"
                print(f"[{i+1}/{len(unique_ceps)}] {status} CEP {cep}")

            # Salvar cache periodicamente
            if (i + 1) % 10 == 0:
                save_cache(cache, cache_file)
                if verbose:
                    print(f"  Cache salvo ({len(cache)} CEPs)")

    # Salvar cache final
    save_cache(cache, cache_file)

    # Adicionar coordenadas ao DataFrame
    df["latitude"] = df["cep_clean"].map(
        lambda x: cache.get(x, (None, None, None))[0] if x and x in cache else None
    )
    df["longitude"] = df["cep_clean"].map(
        lambda x: cache.get(x, (None, None, None))[1] if x and x in cache else None
    )
    df["localidade"] = df["cep_clean"].map(
        lambda x: cache.get(x, (None, None, None))[2] if x and x in cache else None
    )

    if verbose:
        sucessos = sum(1 for v in cache.values() if v is not None)
        print(f"\n✓ Geocodificação completa!")
        print(f"  Total no cache: {len(cache)} CEPs")
        print(f"  Sucessos: {sucessos} ({sucessos/len(cache)*100:.1f}%)")
        print(f"  Projetos com coordenadas: {df['latitude'].notna().sum()}")

    return df


def create_folium_map(
    df: pd.DataFrame,
    output_file: str = "results/mapa_projetos.html",
    center: Tuple[float, float] = (-15.7801, -47.9292),  # Brasília
    zoom_start: int = 11,
) -> "folium.Map":
    """
    Cria um mapa interativo com Folium usando os projetos geocodificados.

    Args:
        df: DataFrame com colunas latitude, longitude, nome, situacao, etc.
        output_file: Caminho para salvar o mapa HTML
        center: Coordenadas do centro do mapa (lat, lon)
        zoom_start: Nível inicial de zoom

    Returns:
        Objeto folium.Map

    Raises:
        ImportError: Se folium não estiver instalado
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        raise ImportError("folium não está instalado. Instale com: pip install folium")

    # Criar mapa
    m = folium.Map(location=center, zoom_start=zoom_start, tiles="OpenStreetMap")

    # Adicionar cluster de marcadores
    marker_cluster = MarkerCluster().add_to(m)

    # Adicionar marcadores para cada projeto
    projetos_com_coords = df[df["latitude"].notna()].copy()

    for idx, row in projetos_com_coords.iterrows():
        nome = str(row.get("nome", "Sem nome"))[:50]
        popup_text = f"""
        <b>{nome}...</b><br>
        CEP: {row.get('cep_clean', 'N/A')}<br>
        Situação: {row.get('situacao', 'N/A')}<br>
        Endereço: {str(row.get('endereco', 'N/A'))[:50]}<br>
        """

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=nome[:30] + "...",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(marker_cluster)

    # Salvar mapa
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    m.save(output_file)

    print(f"Mapa salvo em {output_file}")
    print(f"Total de projetos no mapa: {len(projetos_com_coords)}")

    return m


if __name__ == "__main__":
    # Teste básico
    test_cep = "70040902"  # Congresso Nacional, Brasília
    print(f"Testando geocodificação do CEP {test_cep}")
    result = geocode_cep(test_cep)
    print(f"Resultado: {result}")
