# sportpaper-deployment

Automatically publishes Maven artifacts from the latest
[`Electroid/SportPaper`](https://github.com/Electroid/SportPaper) `main` build to https://repo.pgm.fyi

The workflow runs hourly and publishes only when the upstream
commit changes, and records a commit only after publication succeeds. SportPaper's source and
artifact metadata are not modified.

## Published artifacts

- `app.ashcon:sportpaper-api:1.8.8-R0.1-SNAPSHOT`
- `app.ashcon:sportpaper:1.8.8-R0.1-SNAPSHOT`

