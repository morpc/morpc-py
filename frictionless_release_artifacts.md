# Publishing data as Frictionless packages in GitHub Releases

*A proposal for how MORPC pipelines should publish their data outputs. Context: [issue #159](https://github.com/morpc/morpc-py/issues/159).*

## The problem

Today, large build outputs get committed into the data repos themselves, usually through Git LFS. That grows without bound. In `morpc-addresspoints-standardize`, the standardized address-point output is rebuilt on every run and every version is retained in LFS — and LFS bills for both storage *and* bandwidth.

GitHub **release assets** are a better home for these files: a 2 GB per-file limit, and they count against neither the LFS quota nor the repo size. The proposal is to pair that storage with the Frictionless descriptors we already write, so that a released dataset is not just a file on a download page but a **self-describing package** a colleague can load, validate, and trust from a single URL.

## How a Frictionless package maps onto a GitHub repo

The two systems line up cleanly:

| Frictionless | GitHub | What it holds |
|---|---|---|
| **Package** (`.package.yaml`) | one **Release** (a tag, e.g. `v2026.7.22`) | The manifest for a versioned, frozen snapshot |
| **Resource** (`.resource.yaml`) | one attached **asset** | One data file + its schema, byte size, and hash |
| Schema (`.schema.yaml`) | committed in the **repo** | Column names, types, descriptions |

The **repository** holds the code, schemas, and the small text descriptors — it is mutable and moves with every commit. A **release** is an immutable, tagged snapshot that also carries the heavy data files as assets. Once published, that version never changes.

The important property: a release-asset URL is **fully determined by `(owner, repo, tag, filename)`**:

```
https://github.com/morpc/morpc-addresspoints-standardize/releases/download/v2026.7.22/addresspoints.gpkg
```

So you can write the URL into a descriptor *before* the release exists — as long as you pick the tag first.

---

## What is built today vs. what issue #159 needs

This matters for the pitch, because **the release-asset workflow does not work end-to-end yet.** The three core functions exist and are solid, but every one of them currently assumes `path` points at a **local file**. Here is the honest split.

### Built today (works now, for local data)

- **`create_resource(dataPath, ..., writeResource=True)`** writes a `.resource.yaml` for a local data file. It infers format/mediatype from the extension, attaches the schema, and computes an **MD5** `hash` and `bytes` by reading the file at `os.path.join(os.path.dirname(resourcePath), dataPath)`.
- **`create_package(dir, resources, name, version, keywords)`** bundles a list of resource files into one `.package.yaml`. It coerces `version` through `packaging.Version`; unpadded CalVer like `2026.7.22` round-trips unchanged.
- **`load_data(resourcePath, ...)`** reads a local resource file, resolves the data as `os.path.join(sourceDir, resource.path)`, and casts every column to its schema type.
- **GitHub Releases** themselves (via the web UI or `gh` CLI) already exist — that part is just GitHub.

### Requires issue #159 (not built yet)

The gap is entirely about letting `path` be a **URL** while keeping a local working copy:

| Change | Where | Why it's needed |
|---|---|---|
| Add `cache` and `hashAlgorithm` params to `create_resource` | `frictionless.py:412` | Today hash/bytes are computed by joining the resource dir with `dataPath`. When `path` is a URL, that join is meaningless. `cache` tells it which **local** file to hash/size instead, and gets emitted as `_cache` in the descriptor. `hashAlgorithm` allows `sha256`. |
| Add `morpc.sha256()` | `morpc.py` (sibling to `md5()` at `morpc.py:2975`) | Emit a self-describing `hash: sha256:<hex>` (Data Package v2 form) instead of the bare MD5. |
| Add a `resolve_data_path()` helper and route `load_data` through it | `frictionless.py:748` (3 call sites) | `load_data` currently does `os.path.join(sourceDir, resource.path)`. With a URL, `os.path.join("output_data", "https://…")` yields `"output_data/https:/…"` — it fails silently. The helper prefers `_cache` if the file is on disk, else downloads the asset, verifies it against `hash`/`bytes`, and returns the local path. |
| *(optional)* Add `.zip` to `EXTENSION_MAP` | `frictionless.py:485` | Published assets will often be gzipped/zipped. |

**The design in one line:** one descriptor names *both* the immutable published URL (`path`) and the local working copy (`_cache`), so the two can never drift. Consumers always get a URL that resolves; local development reads the file already on disk.

Everything below is written as the **target workflow**. Steps are marked ✅ (works today) or 🚧 (depends on #159).

---

## Part 1 — Making a package "release-ready" (in Jupyter)

Example: `morpc-addresspoints-standardize`, a package with **two resources** — a large `addresspoints.gpkg` (the reason we want release assets) and a small `addresspoints_by_county.csv` summary.

### Step 1 — Build the outputs ✅

Nothing changes in your pipeline. Write the outputs to a working directory.

```python
# your pipeline, unchanged — write outputs to ./output_data/
addresspoints.to_file("output_data/addresspoints.gpkg", driver="GPKG")
summary.to_csv("output_data/addresspoints_by_county.csv")
```

### Step 2 — Describe each output as a Resource

`create_resource()` writes a `.resource.yaml` binding each data file to its schema and recording its byte count and checksum.

The **small CSV** lives in both the repo and the release, so its `path` stays a plain filename — this works today ✅:

```python
import morpc.frictionless as frl

frl.create_resource(
    "addresspoints_by_county.csv",
    name="addresspoints_by_county",
    title="Address Points by County",
    schemaPath="addresspoints_by_county.schema.yaml",
    resourcePath="output_data/addresspoints_by_county.resource.yaml",
    writeResource=True,
    validate=True,
)
```

For the **large GeoPackage**, the descriptor's `path` is the future asset URL, and the new `cache` keyword records the local working copy — this is the 🚧 part that needs #159:

```python
tag = "v2026.7.22"
base = f"https://github.com/morpc/morpc-addresspoints-standardize/releases/download/{tag}"

frl.create_resource(
    f"{base}/addresspoints.gpkg",        # authoritative, versioned URL  🚧
    name="addresspoints",
    title="Standardized Address Points",
    schemaPath="addresspoints.schema.yaml",
    cache="addresspoints.gpkg",          # local copy, relative to the resource file  🚧
    hashAlgorithm="sha256",              # 🚧
    resourcePath="output_data/addresspoints.resource.yaml",
    writeResource=True,
)
```

The resulting `addresspoints.resource.yaml` describes one file in two places:

```yaml
name: addresspoints
type: table
path: https://github.com/morpc/morpc-addresspoints-standardize/releases/download/v2026.7.22/addresspoints.gpkg
_cache: addresspoints.gpkg
scheme: https
format: gpkg
hash: sha256:9f2c...           # computed from the local cache file
bytes: 207831044
schema: addresspoints.schema.yaml
```

### Step 3 — Bundle the resources into a Package ✅

`create_package()` collects the resource files into one `.package.yaml` — the manifest for the whole release. This is where **multi-resource** packages come together: list every resource you want shipped under one tag.

```python
frl.create_package(
    dir="output_data",
    resources=[
        "addresspoints.resource.yaml",
        "addresspoints_by_county.resource.yaml",
    ],
    name="morpc-addresspoints-standardize",
    version="2026.7.22",                 # unpadded CalVer  →  tag v2026.7.22
    keywords=["address", "points", "morpc"],
)
```

> **Watch the version padding.** Use **unpadded** CalVer — `2026.7.22`, not `2026.07.22`. `packaging.Version` silently normalizes the padded form (`2026.07.22` → `2026.7.22`), which would break the tag ↔ version match the asset URL depends on. For a same-day rebuild, use `2026.7.22.1`. No code change is needed here as long as we standardize on unpadded.

---

## Part 2 — Cutting the tag and publishing the release (in the browser) ✅

GitHub Releases already work; nothing here depends on #159. First commit and push the descriptors and schemas, then on **github.com**:

1. Go to the repo → **Releases** → **Draft a new release**.
2. In **Choose a tag**, type `v2026.7.22` and select **Create new tag on publish**.
3. Set a title (`v2026.7.22`) and a short description of what changed.
4. Drag the built files into **Attach binaries**: `addresspoints.gpkg`, `addresspoints_by_county.csv`, both `.resource.yaml` files, and the `.package.yaml`.
5. Click **Publish release**. The tag and every asset URL now exist and are frozen.

The same thing from the terminal (this is also what CI would run):

```bash
gh release create v2026.7.22 --title "v2026.7.22" \
   output_data/addresspoints.gpkg \
   output_data/addresspoints_by_county.csv \
   output_data/*.resource.yaml \
   output_data/*.package.yaml
```

Because you attached files named exactly `addresspoints.gpkg` etc. under tag `v2026.7.22`, the URLs written into the descriptors in Step 2 now resolve. The descriptor and the release agree by construction.

---

## Part 3 — Using a released package (back in Jupyter) 🚧

Point `load_data()` at a resource descriptor's URL. With the #159 changes it downloads the asset, verifies it against the recorded hash and byte count, casts every column to its schema type, and returns a DataFrame.

```python
import morpc.frictionless as frl

base = "https://github.com/morpc/morpc-addresspoints-standardize/releases/download/v2026.7.22"

points  = frl.load_data(f"{base}/addresspoints.resource.yaml")
summary = frl.load_data(f"{base}/addresspoints_by_county.resource.yaml")
```

Because the URL carries the tag, everyone who runs this line gets **byte-for-byte the same data**. Analyses become reproducible: the version is right there in the path. Someone who wants newer data changes one string — `v2026.7.22` → `v2026.7.29` — and nothing else.

> Today, `load_data` only resolves local paths, so this exact call fails until the `resolve_data_path()` helper from #159 lands. The workaround that works now is to download the release assets (and their `.resource.yaml`/`.schema.yaml`) into a local directory and call `load_data` on the local resource file.

---

## Part 4 — Updating a released dataset

Releases are immutable, and that is the point — you never overwrite `v2026.7.22`. Instead you cut a **new** version alongside it; the old one stays valid for anyone who pinned to it.

| Situation | New version | New tag |
|---|---|---|
| Routine refresh a week later | `2026.7.29` | `v2026.7.29` |
| Fix / rebuild on the same day | `2026.7.22.1` | `v2026.7.22.1` |

The loop is just Steps 1–4 again with the new tag string:

1. Rebuild the outputs in the notebook.
2. Re-run `create_resource()` / `create_package()` with the new `tag` and `version` — the URLs and checksums update themselves.
3. Commit and push the changed descriptors.
4. Draft a new release on the new tag and attach the new assets.

Nothing about the old release moves. Downstream code keeps resolving `v2026.7.22` until someone deliberately bumps the tag in their URL — no silent data changes under anyone's feet.

---

## Authentication and GitHub accounts

Most of the friction lives in one distinction: **public vs. private repository**. It decides whether `load_data()` can fetch an asset with no credentials.

- **Public repo — easy.** Release assets download over anonymous HTTPS; no token needed. `load_data(url)` just works, on any laptop. This is the frictionless path and the one this proposal assumes.
- **Private repo — needs a token.** Asset downloads require an authenticated request (a personal access token, or CI's `GITHUB_TOKEN`), which has to be threaded into `load_data`. Prefer public repos for anything meant to be broadly loadable.

**Who needs what:**

- **To publish a release:** a GitHub account that is a member of the `morpc` org with **Write** (or Maintain) access to the repo. The browser flow needs nothing more than being logged in.
- **To publish via `gh` or CI:** a one-time `gh auth login`, or in GitHub Actions the built-in `GITHUB_TOKEN` with `permissions: contents: write` — no personal token to manage.
- **To consume from a public repo:** nothing. No account, no token.

**Two decisions for the team before rolling this out:**

1. Which data repos become **public** (so consumers need no credentials).
2. That we standardize on **unpadded CalVer** tags, so the URL-from-version guarantee holds everywhere.
