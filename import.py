import os
import pathlib
import re
import sys
from typing import Mapping, TypedDict

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
    episode_id: str
    episode_title: str
    speaker: str
    text: str
    line_number: int | None


# Create transcripts collection
create_response = client.collections.create(
    {
        "name": "transcripts",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "podcast", "type": "string", "facet": True},
            {"name": "episode_id", "type": "string", "facet": True},
            {"name": "episode_title", "type": "string"},
            {"name": "speaker", "type": "string", "facet": True},
            {"name": "text", "type": "string"},
            {"name": "line_number", "type": "int32", "optional": True},
        ],
    }
)

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

for podcast, episodes in transcripts_by_podcast.items():
    for index, (episode_title, transcript) in enumerate(episodes):
        episode_id = f"{podcast}_{index}"
        speaker = ""

        lines = [line for line in transcript.splitlines() if line.strip() != ""]
        datas: list[Mapping] = []
        for index, line in enumerate(lines):
            if match := SPEAKER_PATTERN.match(line):
                speaker = match.groups()[0]
                line = line[match.regs[0][1] :]

            line_number = index + 1
            id = f"{episode_id}_{line_number}"

            data = TranscriptLine(
                id=id,
                podcast=podcast,
                episode_id=episode_title,
                episode_title=title,
                speaker=speaker,
                text=line,
                line_number=line_number,
            )
            datas.append(data)

        doc = client.collections["transcripts"].documents.import_(
            datas, import_parameters={"action": "upsert"}
        )
        print(f"imported {episode_title}")
