import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { CALIBRATION, multiplier } from "../site/simple_model.js";

const fixture = JSON.parse(
  readFileSync(new URL("../site/data/simple_fixture.json", import.meta.url)),
);

test("JavaScript matches Python on every fixture row", () => {
  assert.ok(fixture.length > 100);
  for (const row of fixture) {
    const actual = multiplier(row.alpha, row.financing, row.state, row.params);
    if (row.expected === null) {
      assert.equal(actual, null);
    } else {
      assert.ok(Math.abs(actual - row.expected) < 1e-9, JSON.stringify(row));
    }
  }
});

test("calibration matches the thesis", () => {
  assert.equal(CALIBRATION.kappa, 0.03);
  assert.equal(CALIBRATION.p, 0.8);
});

test("unknown financing is rejected", () => {
  assert.throws(() => multiplier(0, "debt", "normal"));
});
