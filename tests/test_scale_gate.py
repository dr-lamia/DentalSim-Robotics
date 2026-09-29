from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from dentalsim.scale_gate import physical_scale_available


def test_scale_gate_closed_by_default(tmp_path):
    assert not physical_scale_available(None)
    assert not physical_scale_available(tmp_path/"missing.json")


def test_scale_gate_requires_positive_hash_locked_scale(tmp_path):
    p=tmp_path/"scale.json"
    p.write_text(json.dumps({
      "status":"physical_scale_calibrated",
      "mesh_sha256":"abc",
      "scale_mm_per_native_unit":0.2
    }))
    assert physical_scale_available(p,"abc")
    assert not physical_scale_available(p,"different")
