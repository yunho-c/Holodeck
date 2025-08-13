"""
A minimalistic script to download 3D models from Objaverse-XL
based on a list of asset IDs.
"""

import objaverse.xl as oxl
import pandas as pd
from typing import List
import os

print("Getting Objaverse-XL annotations...")
annotations = oxl.get_annotations()


def download_assets(asset_ids: List[str]):
    """
    Downloads 3D assets from Objaverse-XL based on a list of asset IDs.

    Args:
        asset_ids (List[str]): A list of asset IDs to download.
        prepend_path (bool): If True, prepends '~/.objaverse' to the file paths.
    """
    print(f"Filtering annotations for {len(asset_ids)} asset IDs...")

    # The asset IDs from the retriever are typically part of the 'fileIdentifier' URL.
    # We can filter the DataFrame by checking if any of the asset IDs are in the 'fileIdentifier'.

    # Per pandas performance best practices, we first extract the IDs using a
    # vectorized operation, then filter using the highly-optimized .isin() method.
    annotations["extracted_id"] = annotations["fileIdentifier"].str.extract(
        r"([a-f0-9]{32})"
    )
    asset_ids_set = set(asset_ids)
    filtered_annotations = annotations[annotations["extracted_id"].isin(asset_ids_set)]

    if filtered_annotations.empty:
        print(
            "Could not find any of the provided asset IDs in the Objaverse-XL annotations."
        )
        return
    # filtered_annotations = annotations  # DEBUG

    print(f"Found {len(filtered_annotations)} matching objects. Starting download...")

    downloaded_files = oxl.download_objects(filtered_annotations, processes=2)

    # if prepend_path:
    #     home_dir = os.path.expanduser("~")
    #     objaverse_dir = os.path.join(home_dir, ".objaverse")
    #     downloaded_files = {
    #         uid: os.path.join(objaverse_dir, path)
    #         for uid, path in downloaded_files.items()
    #     }

    print("\nDownloaded files:")
    for uid, path in downloaded_files.items():
        print(f"  {uid}: {path}")

    return downloaded_files


def test():
    # Example from the user's prompt
    results = [
        ("bc1a438ca9af413fa93bd56e9bdbb01c", 32.4226188659668),
        ("53b4bf049dec4e21963706f60b9ebdb7", 32.417179107666016),
        ("Sofa_204_1", 32.33254623413086),
        ("Sofa_207_5", 32.26934814453125),
        ("0b74f256116d4096992f3f8ecc2a8ca8", 32.20747756958008),
        ("a82cf2f38ca549ed87982f422b9fb092", 31.98259162902832),
        ("e373d930b7d34ad69d813b22561f7218", 31.84498405456543),
        ("26e5c4efc819479c851042b6199aec4e", 31.829191207885742),
        ("b9a278fd09a748b4bed92eb0a2264a80", 31.76921844482422),
        ("Sofa_210_1", 31.72628402709961),
    ]

    # Extract asset_ids from the results
    asset_ids_to_download = [result[0] for result in results]

    # Filter out non-objaverse UIDs (heuristic: check length of hex string)
    objaverse_uids = [
        uid
        for uid in asset_ids_to_download
        if len(uid) == 32 and all(c in "0123456789abcdef" for c in uid)
    ]

    print(f"Attempting to download {len(objaverse_uids)} objects from Objaverse-XL...")
    download_assets(objaverse_uids, prepend_path=False)


if __name__ == "__main__":
    test()
