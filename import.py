import os
import pathlib
import re
import sys
from typing import Mapping, TypedDict

import typesense.exceptions
from typesense.client import Client
from typesense.configuration import ConfigDict

curr_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.abspath(os.path.join(curr_dir, os.pardir)))


conf = ConfigDict(
    api_key=os.environ["TS_API_KEY"],
    nodes=[
        {
            "host": os.environ.get("TS_HOST", "localhost"),
            "port": int(os.environ.get("TS_PORT", "8108")),
            "protocol": os.environ.get("TS_PROTO", "http"),
        }
    ],
    timeout_seconds=int(os.environ.get("TS_TIMEOUT", "2")),
)
client = Client(conf)

# Drop pre-existing collection if any
if "TS_DROP" in os.environ:
    try:
        client.collections["transcripts"].delete()
    except Exception:
        pass


class TranscriptLine(TypedDict):
    id: str
    podcast: str
    episode: int
    speaker: str
    text: str
    line_number: int | None


# Create transcripts collection
try:
    create_response = client.collections.create(
        {
            "name": "transcripts",
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "podcast", "type": "string", "facet": True},
                {"name": "episode", "type": "int32", "facet": True},
                {"name": "speaker", "type": "string", "facet": True},
                {"name": "text", "type": "string"},
                {"name": "line_number", "type": "int32", "optional": True},
            ],
        }
    )
except typesense.exceptions.ObjectAlreadyExists:
    pass

# Add transcripts
path = pathlib.Path("../changelog-transcripts")
transcripts_by_podcast: dict[str, list[tuple[str, str]]] = {}
for path in path.glob("*/*.md"):
    paths = str(path).split("/")
    title = paths[-1].replace(".md", "")
    podcast = paths[-2]
    with open(path) as fin:
        transcript = fin.read()
    if podcast not in transcripts_by_podcast:
        transcripts_by_podcast[podcast] = []
    transcripts_by_podcast[podcast].append((title, transcript))

SPEAKER_PATTERN = re.compile(r"\*\*(.*):\*\*\s*")


def get_episode_number(filename: str) -> int:
    try:
        return int(filename.split("-")[-1])
    except (IndexError, ValueError):
        print(f"could not parse episode number: {filename}")
        return 0


for podcast, episodes in transcripts_by_podcast.items():
    # sort episodes in order
    episodes = sorted(
        episodes,
        key=lambda title_and_transcript: get_episode_number(title_and_transcript[0]),
    )
    for episode_title, transcript in episodes:
        episode = get_episode_number(episode_title)
        speaker = ""

        lines = [line for line in transcript.splitlines() if line.strip() != ""]
        datas: list[Mapping] = []
        for index, line in enumerate(lines):
            if match := SPEAKER_PATTERN.match(line):
                speaker = match.groups()[0]
                line = line[match.regs[0][1] :]

            line_number = index + 1
            id = f"{podcast}_{episode}_{line_number}"

            data = TranscriptLine(
                id=id,
                podcast=podcast,
                episode=episode,
                speaker=speaker,
                text=line,
                line_number=line_number,
            )
            datas.append(data)

        doc = client.collections["transcripts"].documents.import_(
            datas, import_parameters={"action": "upsert"}
        )
        print(f"imported {episode_title}")
