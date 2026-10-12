# tools

Scripts used to build the point clouds (kept for reference; they expect the original
PLY files from Mario's computer next to them).

- `conv.py`, `conv2.py`, `conv3.py` – thin the source scans (forest, outdoor scan, steel frame) with a voxel grid
- `church.py` – generates the St. Mauritius concert-hall cutaway model from plan, section and model photo (metres)
- `build6.py` – scales all clouds, pairs their points spatially (kd-tree order) so they can morph, and encodes them
- `export.py` – turns the single-file prototype into this site (clouds and images as separate files)

Cloud file format (`*.bin`): n×int16 x, n×int16 y, n×int16 z (scale 1/4000), then n×uint8 weight.
