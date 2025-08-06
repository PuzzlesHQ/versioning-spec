import json
import os
import subprocess
import time
import datetime

# required since it executes differently depending on where the main file is called from
try:
    # python3 main.py
    import git
    import gradle
except:
    # python3 versioning/main.py
    import versioning.git
    import versioning.gradle

git.init_credentials("github-actions", "github-actions@github.com")
git.checkout("versioning", "orphan")
git.reset()
git.pull(branch_name="versioning")

def findPhase(ver):
    if "-a" in ver: return "alpha"
    if "-b" in ver: return "beta"
    if "-rc" in ver: return "release-candidate"
    return "release"

repoUrl = f"https://github.com/{os.getenv("GITHUB_REPO")}"

username = os.getenv("GITHUB_USERNAME")
email = os.getenv("GITHUB_EMAIL")
version = (os.getenv("GITHUB_REF") or "refs/tags/0.0.0-alpha").replace("refs/tags/", "")
phase = findPhase(version)

f = open("versions.json", "r")
contents = f.read()
f.close()

config = open("config.json", "r")
cfg = json.loads(f.read())
config.close()

contents = json.loads(contents)

contents["latest"]["*"] = version
contents["latest"][phase] = version

if not phase in contents["existing-phases"]:
    contents["existing-phases"].append(phase)

contents["versions"][version] = {
    "epoch": int(time.time()),
    "date": datetime.datetime.now().astimezone(datetime.timezone.utc).strftime("%Y/%m/%dT%H:%M:%S"),
    "id": version,
    "phase": phase
}

if cfg["uses-maven-central"]: contents["versions"][version]["maven-central"] = cfg["maven-central-location"] + version
if cfg["uses-jitpack"]: contents["versions"][version]["maven-jitpack"] = cfg["jitpack-location"] + version
if cfg["uses-gradle-dependencies-json"]: contents["versions"][version]["dependencies"] = f"{repoUrl}/releases/download/{version}/dependencies.json"

f = open("versions.json", "w")
f.write(json.dumps(contents, indent="\t"))
f.close()

if cfg["uses-gradle-dependencies-json"]:
    gradle.run(task_name="mkDeps")
    subprocess.call(args=["gh", "release", "upload", version, "./dependencies.json"])
git.commit(f"add {version} to version manifest", "versions.json")
git.push(branch_name="versioning")