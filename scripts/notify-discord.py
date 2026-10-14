#!/usr/bin/env python3
import datetime
import json
import os
import sys
import urllib.request

def payload():
    env = os.environ
    project = env["NOTIFY_PROJECT"]
    status = env["NOTIFY_STATUS"]
    sha = env["UPSTREAM_SHA"]
    run_url = "{}/{}/actions/runs/{}".format(
        env.get("GITHUB_SERVER_URL", "https://github.com"),
        env["GITHUB_REPOSITORY"], env["GITHUB_RUN_ID"])
    commit_url = "https://github.com/{}/commit/{}".format(env["UPSTREAM_REPOSITORY"], sha)
    fields = [
        {"name": "Commit", "value": "[`{}`]({})".format(sha[:7], commit_url), "inline": True},
        {"name": "Branch", "value": "`{}`".format(env["UPSTREAM_BRANCH"]), "inline": True},
    ]
    repo_link = "[PGM Repo](https://repo.pgm.fyi)"
    started = env.get("BUILD_STARTED_AT")
    if status != "started" and started:
        seconds = max(0, int(datetime.datetime.now(datetime.timezone.utc).timestamp()) - int(started))
        fields.append({"name": "Duration", "value": "{}m {}s".format(seconds // 60, seconds % 60), "inline": True})
    if status == "started":
        title = project + " · Build started"
        description = "Building the latest {} commit for publication to {}.".format(project, repo_link)
        color = 3447003
        fields.append({"name": "Trigger", "value": "Scheduled" if env.get("GITHUB_EVENT_NAME") == "schedule" else "Manual", "inline": True})
    elif status == "success":
        title = project + " · Published successfully"
        description = "The latest {} build is now available on {}.".format(project, repo_link)
        color = 3066993
        artifact_links = []
        public_repository = env.get("PUBLIC_REPOSITORY_URL", "https://repo.pgm.fyi/snapshots").rstrip("/")
        for coordinate in env["NOTIFY_ARTIFACTS"].splitlines():
            if coordinate:
                group, artifact, version = coordinate.split(":")
                artifact_url = "{}/{}/{}/{}/".format(public_repository, group.replace(".", "/"), artifact, version)
                artifact_links.append("[`{}`]({})".format(coordinate, artifact_url))
        fields.append({"name": "Artifacts", "value": "\n".join(artifact_links)})
    else:
        title = project + " · Publication to PGM Repo failed"
        description = "{} could not be published to {}. The next scheduled check will retry.".format(project, repo_link)
        color = 15158332
        if env.get("PUBLISH_OUTCOME") == "success":
            description = "Artifacts were published to {}, but recording the successful commit failed. The next scheduled check will retry.".format(repo_link)
        stage = "Build environment setup"
        for name, key in [("Build SportPaper", "BUILD_OUTCOME"), ("Build and publish to PGM Repo", "PUBLISH_OUTCOME"), ("Record successful publication", "STATE_OUTCOME")]:
            if env.get(key) == "failure":
                stage = name
        fields.append({"name": "Failed stage", "value": stage})
    label = "View failed run" if status == "failure" else "View workflow run"
    fields.append({"name": "Workflow", "value": "[{}]({})".format(label, run_url)})
    return {"allowed_mentions": {"parse": []}, "embeds": [{
        "title": title, "url": run_url, "description": description, "color": color,
        "fields": fields, "footer": {"text": "PGM Repo · Forced rebuild" if env.get("FORCE_PUBLISH") == "true" else "PGM Repo"},
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }]}

def main():
    preview = "--preview" in sys.argv
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook and not preview:
        print("Discord webhook is not configured; skipping notification.")
        return
    body = json.dumps(payload()).encode()
    if preview:
        print(body.decode())
        return
    # Wait for confirmation; discard response and never print the secret URL or errors containing it.
    url = webhook + ("&" if "?" in webhook else "?") + "wait=true"
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "PGM-Repo-Publisher/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read()
        print("Discord notification sent.")
    except Exception:
        print("::warning::Discord notification could not be delivered.")

if __name__ == "__main__":
    main()
