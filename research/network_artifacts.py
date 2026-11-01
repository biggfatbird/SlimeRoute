"""Masks carry explicit geometry identities and a content checksum, never an implicit edge order."""
from pathlib import Path
import hashlib
import numpy as np


def save_masks(path, geo, **masks):
    path = Path(path)
    for mask in masks.values():
        if mask.dtype != bool or mask.shape != geo["I"].shape:
            raise ValueError("Expected one boolean per candidate edge")
    if path.suffix == ".npy":
        if len(masks) != 1:
            raise ValueError("NPY requires one mask")
        np.save(path, next(iter(masks.values())))
    else:
        np.savez_compressed(path, **masks)
    np.savez_compressed(str(path) + ".identity.npz", pts=geo["pts"],
                        edges=np.column_stack((geo["I"], geo["J"])),
                        sha256=np.array(hashlib.sha256(path.read_bytes()).hexdigest()))


def load_masks(path, geo):
    path = Path(path)
    identity = Path(str(path) + ".identity.npz")
    if not identity.exists():
        raise ValueError(f"Missing edge identity for {path.name}; regenerate, do not guess historical edge order")
    with np.load(identity, allow_pickle=False) as meta:
        if str(meta["sha256"]) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("Mask checksum mismatch")
        if meta["pts"].shape != geo["pts"].shape or not np.allclose(meta["pts"], geo["pts"], rtol=0, atol=1e-9):
            raise ValueError("Mask node coordinates differ from current geometry")
        edges = meta["edges"]
    current = np.column_stack((geo["I"], geo["J"]))
    if edges.shape != current.shape:
        raise ValueError("Mask edge set differs from current geometry")
    keys = [tuple(sorted(e)) for e in edges.tolist()]
    lookup = {edge: i for i, edge in enumerate(keys)}
    try:
        order = np.array([lookup[tuple(sorted(e))] for e in current.tolist()])
    except KeyError as exc:
        raise ValueError("Mask edge set differs from current geometry") from exc
    if len(lookup) != len(edges) or len(np.unique(order)) != len(edges):
        raise ValueError("Duplicate or missing edge identities")
    if path.suffix == ".npy":
        raw = {"mask": np.load(path, allow_pickle=False)}
    else:
        with np.load(path, allow_pickle=False) as z:
            raw = {k: z[k] for k in z.files}
    for k, m in raw.items():
        if m.dtype != bool or m.shape != (len(edges),):
            raise ValueError(f"Invalid mask {k}")
    return {k: m[order] for k, m in raw.items()}


def load_mask(path, geo):
    return load_masks(path, geo)["mask"]
