# publish-vsixgallery

A GitHub Action to publish **Visual Studio** (the IDE) extensions (.vsix) to the [Open VSIX Gallery](https://www.vsixgallery.com). This is not for VS Code extensions.

Works on both **Linux** and **Windows** runners. Uses `curl` and `bash` — no PowerShell or extra dependencies required.

## Usage

```yaml
- name: Publish to Open VSIX Gallery
  uses: madskristensen/publish-vsixgallery@v1
  with:
    vsix-file: path/to/MyExtension.vsix
```

After a successful upload the action writes a workflow run summary containing the gallery badge, the extension page link, and a **manage link** that lets you delete the extension yourself from the gallery.

## Inputs

| Input | Description |
|-------|-------------|
| `vsix-file` | Path to the `.vsix` file to upload |
| `readme` | URL to a `README.md` for the gallery listing. Defaults to `<branch>/README.md` in the current repo |
| `manage-token` | Optional. Acts as a password for the extension's `/extension/<id>/manage` page (used to delete the extension). See [Manage tokens](#manage-tokens) below. |
| `gallery-url` | Optional. Base URL of the gallery to publish to. Defaults to `https://www.vsixgallery.com`. Override this if you host your own instance of the Open VSIX Gallery. |

## Manage tokens

Every extension can be deleted from its gallery manage page (`https://www.vsixgallery.com/extension/<id>/manage`). Access is gated by a per-extension **manage token** — it's a soft "don't let randos delete my listing" speed bump, not strong authentication.

- **First upload, no `manage-token` supplied:** the gallery auto-generates a token and embeds it in the manage URL printed in the workflow run summary. **Save that URL** — the token isn't shown anywhere else.
- **First upload, `manage-token` supplied:** the gallery uses the value you supply (typically a GitHub Actions secret). The manage URL won't contain it.
- **Republish, no `manage-token`:** the existing token stays in place. The manage URL won't contain it.
- **Republish, `manage-token` supplied:** the value you pass becomes the new manage token, replacing whatever was on file. Lost your old token? Just republish with a fresh one and the new value takes over.

The token is always masked in workflow logs.

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
          manage-token: ${{ secrets.VSIXGALLERY_MANAGE_TOKEN }}
```
