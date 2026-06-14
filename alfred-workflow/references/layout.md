# Canvas Layout (uidata)

The canvas is the user's primary mental model of the workflow — they will open it in
Alfred's editor. Overlapping or zigzagging nodes read as broken even when the graph
works. Numbers below were derived from official alfredapp workflows.

## Schema

```xml
<key>uidata</key>
<dict>
    <key>OBJECT-UID</key>
    <dict>
        <key>xpos</key><real>60</real>
        <key>ypos</key><real>60</real>
        <key>note</key><string>What this node does</string>   <!-- optional -->
        <key>colorindex</key><integer>9</integer>             <!-- optional -->
    </dict>
</dict>
```

Every object needs an entry; an object without one lands at (0,0) on top of others.
`<real>` and `<integer>` coordinates are both accepted; Alfred 5 writes `<real>`.

## Grid algorithm

Footprints differ by object type (these are what the bundled validator checks for
true overlaps, so honor them):
- **Standard object** (icon + title): ≈120×110 px. A `note` adds a label row, ≈+35 px.
- **Automation / hexagon tiles** — Automation Task, Run Shortcut, System Command,
  Music Command — render ≈180×190 px (about 3× taller).
- **Conditional** grows with outputs: ≈90 + 50·(conditions + else). A 2-branch
  Conditional is ≈240 px tall.
- **Junction** is a small ≈70×60 icon — but still give it its own column slot (below).

Place objects on this grid:

1. **Column = graph depth.** Column of a node = longest path from any trigger/input
   that reaches it. Triggers/inputs sit in column 0; every edge must point to a
   strictly higher column so the graph reads left→right.
2. **x = 60 + 200·column.**
3. **Row = chain.** Each independent chain (per trigger/input) gets a row:
   **y = 60 + 150·row.** A linear chain keeps the SAME ypos across all its nodes —
   straight wires look intentional.
4. **Branch fan-out** (Conditional outputs, modifier-key edges): keep the source at
   its chain's y and give each destination its own row — fan by the row pitch
   (**Δy ≥ 150**, the else branch lowest), not a tight ±70. A 150-tall tile only needs
   ~110 of clearance, but spacing to the row grid keeps wires straight and leaves room
   for notes; branches landing on Automation/hexagon tiles need **Δy ≥ 200**. Negative
   coordinates render fine — if a fan climbs above y≈−100, move the whole chain down.
5. **Merges** (several edges into one node): place the destination at the average y of
   its sources, snapped to the grid.
6. **Never overlap.** The validator flags any true intersection of the footprints
   above — two nodes in one column collide unless |Δy| ≥ their height (≈110 plain,
   ≈145 with a note, ≈190 for an Automation/hexagon tile); two in one row collide
   unless |Δx| ≥ their width (≈120, ≈180 for a hexagon tile). That is only the floor;
   the recommended grid (Δx 200 / Δy 150) clears it with margin, so stay on the grid
   for readability rather than hugging the minimum. This applies to *every* node,
   including ones whose icon looks small:
   - **A Junction occupies a full column slot.** Never tuck it inside a neighbor's
     column between two nodes — its small icon still collides with the big tile around
     it. Give it its own x (Δx ≥ 180 from both sides).
   - **Stacked terminal outputs** (Notification, Large Type, Copy to Clipboard…) sharing
     a column each need a full row (Δy ≥ 150). Bunching them at one x is the most common
     overlap.

When chains are dense, compress rows toward Δy ≈ 130 for plain (note-less) nodes — but
keep Δy ≥ 150 wherever nodes carry notes, or they overlap.

## Notes and colors

- `note` renders as a label under the node. Official workflows label every nontrivial
  node ("Create timer hotkey", "List shortcuts by folder name"). Label at least each
  chain's entry node and any non-obvious utility.
- `colorindex` tints the node frame (observed: 9 teal for triggers, 12 purple for
  hotkeys, 5–7 misc). Optional; use sparingly to group related chains, not decorate.

## Quick checklist

- [ ] Every object uid has a uidata entry; no orphan entries.
- [ ] Edges all point left→right (dest column > source column).
- [ ] Linear chains share a ypos; branches fan by a full row (≥150).
- [ ] Junctions sit in their own column; stacked outputs each get a full row.
- [ ] `validate.py` reports no canvas overlap.
- [ ] Entry nodes carry a `note`.
