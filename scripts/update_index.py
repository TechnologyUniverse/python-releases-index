import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

BASE_FTP = "https://www.python.org/ftp/python/"
BASE_RELEASE = "https://www.python.org/downloads/release/"


def fetch_versions():
    html = requests.get(BASE_FTP, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    versions = []
    for a in soup.find_all("a"):
        v = a.text.strip("/")
        if re.fullmatch(r"\d+\.\d+(\.\d+)?", v):
            versions.append(v)
    return versions


def fetch_release_date(version):
    slug = "python-" + version.replace(".", "")
    url = BASE_RELEASE + slug + "/"

    r = requests.get(url)
    if r.status_code != 200:
        return "—"

    soup = BeautifulSoup(r.text, "html.parser")
    time_tag = soup.find("time")
    return time_tag.text.strip() if time_tag else "—"


def fetch_installers(version):
    url = BASE_FTP + version + "/"
    r = requests.get(url)

    if r.status_code != 200:
        return "—", "—"

    soup = BeautifulSoup(r.text, "html.parser")

    win = "—"
    mac = "—"

    for a in soup.find_all("a"):
        name = a.text.lower()
        link = url + a.text

        if name.endswith(".exe") and ("amd64" in name or "win32" in name):
            win = link

        if name.endswith(".pkg") and "macos" in name:
            mac = link

    return win, mac


def write_markdown(group, versions):
    versions.sort(key=lambda s: list(map(int, s.split("."))), reverse=True)
    path = f"releases/python-{group}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Python {group} Releases\n\n")
        f.write("| Version | Release date | Windows | macOS | Source |\n")
        f.write("|--------|--------------|---------|-------|--------|\n")

        for v in versions:
            date = fetch_release_date(v)
            win, mac = fetch_installers(v)
            f.write(f"| {v} | {date} | {win} | {mac} | {BASE_FTP}{v}/ |\n")


def main():
    versions = fetch_versions()
    groups = defaultdict(list)

    for v in versions:
        major = v.split(".")[0]
        if major in ("2", "3"):
            groups[f"{major}.x"].append(v)

    for group, items in groups.items():
        write_markdown(group, items)

    print("Auto-generated Python 2.x and 3.x with release dates and installers")


if __name__ == "__main__":
    main()
