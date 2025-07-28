py-spy Flamegraph — Markdown Summary

Command: py-spy record -o mkdocs-profile.svg -- poetry run mkdocs build --clean
Total samples: 3,715
Reminder: Flamegraph values are inclusive. Don’t add percentages across overlapping stacks.

⸻

Top Hotspots (directional)

Area / group	Notable frames (file:line)	%
MkDocs config & Markdown extension loading	build_command (mkdocs/main.py:285) 5.71; load_config 5.57; validate 5.57; config_options.validate 5.55; run_validation 5.46; markdown.registerExtensions 5.46; build_extension → import_module 5.41	~25.3
Image pipeline (Pillow/WebP)	has_transparent_edges 4.12; PIL.Image.convert 3.74; WebPImagePlugin.load/_get_next 3.39; another WebP load 1.59; second convert 1.75; __array_interface__ 0.51; tobytes 0.24	~15–17
foe_foundry markdown package imports	foe_foundry_data/markdown/md.py chain 4.93; foe_foundry_data/refs/__init__.py chain 4.93; foe_foundry_data/markdown/__init__.py 5.41 (overlaps)	~10.8
Refs & monsters import graphs	monster_ref.py:11 2.31; monster_ref.py:7 2.48; numerous _find_and_load* 0.19–2.13	~7.6
Runtime generation & data	from_monster 5.11; from_power 2.91; _get_best_statblock 2.77; one_of_each_monster 1.27; generate_monster 1.18; generate 1.05/0.81/0.24; modify_stats 0.57 (+ smaller); copy/deepcopy ~0.70 combined	—
inflect + typeguard AST instrumentation (import-time)	<module> inflect 2.37; many engine(...) and typeguard visit/generic_visit calls 0.11–0.22 each	~3.2–4.0
Cleanup / misc.	shutil.rmtree 0.54 + 0.46 ≈ 1.0; cairosvg/cairocffi/cffi cdef/parse ~0.8; pandas import ~0.5; GitPython commit date lookups many 0.11 slices (~0.4–0.6 total)	—


⸻

What’s actually costing you
	•	Startup/import storms dominate. MkDocs validation + Markdown/Jinja extensions + your foe_foundry_* packages account for a large chunk before any real work happens.
	•	Images are expensive. WebP decoding and repeated convert()/tobytes() and transparency checks are a major CPU sink.
	•	Import-time computation. inflect initialization, typeguard AST instrumentation, GitPython lookups, and top-level module work add overhead.

⸻

Quick wins
	1.	Trim/Delay Extensions
	•	Disable unused Markdown/Jinja extensions.
	•	Lazy-import heavy modules inside extension hooks (extendMarkdown, render functions) instead of at import time.
	2.	Cache Image Results
	•	Precompute transparency flags and store sidecars (e.g., image -> has_transparent_edges JSON).
	•	Batch-convert assets once (WebP → target mode) and reuse cached outputs.
	3.	Move work out of module top-levels
	•	Defer loading large reference datasets and registries until first use.
	•	Replace broad from X import * trees with targeted, on-demand loaders.
	4.	Turn off typeguard for builds
	•	Make decorators no-op via env flag for production/docs builds.
	5.	Memoize Git metadata
	•	Cache commit dates per path; or bake them into data files at authoring time.
	6.	Avoid full cleans in dev
	•	Use incremental builds; if cleaning, purge only changed subdirs rather than whole site/.

⸻

Medium-term refactors
	•	Create a lazy registry layer for foe_foundry_data.* that exposes lookups but imports modules on demand.
	•	Separate build-time data generation from MkDocs import path. Generate JSON once, then have MkDocs read the JSON.
	•	Image metadata fast-paths: when only dimensions/alpha are needed, avoid full convert()/buffer creation.

⸻

Notes
	•	Percentages are inclusive and overlap; treat group totals as directional priorities.
	•	The biggest wins will likely come from:
	1.	Image pipeline caching, and
	2.	Cutting import-time work (extensions + foe_foundry_* data + typeguard/inflect).