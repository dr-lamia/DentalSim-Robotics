#!/usr/bin/env python3
"""Forced-contact negative test for the Case-15 Isaac engineering scene.

Success means contact is detected and the safety contract rejects the rollout.
A 'clean' pass with no contact is a TEST FAILURE.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": True})

import numpy as np  # noqa: E402
import omni.timeline  # noqa: E402
import omni.usd  # noqa: E402
from isaacsim.sensors.experimental.physics import Contact, ContactSensor  # noqa: E402
from pxr import Gf, UsdGeom  # noqa: E402


BUR = "/World/Dental/Bur"
PROTECTED = "/World/Dental/ProtectedSideA"
SENSOR_PATH = BUR + "/ContactSensor"


def _world_center(stage, prim_path):
    cache = UsdGeom.BBoxCache(
        Usd.TimeCode.Default(),
        [UsdGeom.Tokens.default_, UsdGeom.Tokens.render, UsdGeom.Tokens.proxy],
        useExtentsHint=True,
    )
    box = cache.ComputeWorldBound(stage.GetPrimAtPath(prim_path)).ComputeAlignedBox()
    mn = box.GetMin()
    mx = box.GetMax()
    return np.array([(mn[i] + mx[i]) * 0.5 for i in range(3)], dtype=float)


def _bur_translate_op(stage):
    xf = UsdGeom.Xformable(stage.GetPrimAtPath(BUR))
    for op in xf.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            return op
    return xf.AddTranslateOp()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=Path, required=True)
    p.add_argument("--steps", type=int, default=180)
    p.add_argument("--settle-steps", type=int, default=30)
    p.add_argument("--result-json", type=Path, default=Path("forced_contact_result.json"))
    args = p.parse_args()

    try:
        ctx = omni.usd.get_context()
        if not ctx.open_stage(str(args.stage.resolve())):
            raise RuntimeError(f"Could not open {args.stage}")
        for _ in range(10):
            app.update()
        stage = ctx.get_stage()

        if not stage.GetPrimAtPath(BUR).IsValid():
            raise RuntimeError("Bur prim missing")
        if not stage.GetPrimAtPath(PROTECTED).IsValid():
            raise RuntimeError("ProtectedSideA prim missing")

        sensor = ContactSensor(
            Contact.create(
                SENSOR_PATH,
                min_threshold=0.0,
                max_threshold=1.0e9,
                translations=np.array([[0.0, 0.0, 0.0]], dtype=np.float32),
            )
        )

        start = _world_center(stage, BUR)
        target = _world_center(stage, PROTECTED)
        op = _bur_translate_op(stage)

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        for _ in range(args.settle_steps):
            app.update()

        detected = False
        detected_step = None
        raw_count = 0

        for i in range(args.steps + 1):
            alpha = i / max(1, args.steps)
            p3 = start * (1.0 - alpha) + target * alpha
            op.Set(Gf.Vec3d(float(p3[0]), float(p3[1]), float(p3[2])))
            app.update()

            raw = sensor.get_raw_data()
            try:
                n = len(raw)
            except TypeError:
                n = 0
            if n > 0:
                detected = True
                detected_step = i
                raw_count = n
                break

        timeline.stop()

        result = {
            "test": "forced_protected_contact_negative_test",
            "contact_detected": detected,
            "contact_step": detected_step,
            "raw_contact_records": raw_count,
            "safety_rollout_accepted": False if detected else None,
            "pass": bool(detected),
            "interpretation": (
                "PASS: protected contact was detected and rollout must be rejected."
                if detected
                else "FAIL: the bur reached the protected target without a detected contact."
            ),
        }
        args.result_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))

        if not detected:
            raise SystemExit(3)
    finally:
        app.close()


if __name__ == "__main__":
    main()
