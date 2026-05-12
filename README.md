# publish-vsixgallery

A GitHub Action to publish Visual Studio extensions (.vsix) to the [Open VSIX Gallery](https://www.vsixgallery.com).

Works on both **Linux** and **Windows** runners. Uses `curl` and `bash` — no PowerShell or extra dependencies required.

## Usage

```yaml
- name: Publish to Open VSIX Gallery
  uses: madskristensen/publish-vsixgallery@v1
  with:
    vsix-file: path/to/MyExtension.vsix
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `vsix-file` | ✅ | Path to the `.vsix` file to upload |
| `readme` | ❌ | URL to a `README.md` for the gallery listing. Defaults to `<branch>/README.md` in the current repo |

## Example workflow

```yaml
jobs:
  publish:
    runs-on: windows-latest
    needs: build
    steps:
      - uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: MyExtension.vsix

      - name: Publish to Open VSIX Gallery
        uses: madskristensen/publish-vsixgallery@v1
        with:
          vsix-file: MyExtension.vsix
```