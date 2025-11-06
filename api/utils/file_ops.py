import os
import yaml
from datetime import date


def read_event_file(year, month, week):
    # Implement reading event file
    pass


def write_event_file(year, month, week, event_data):
    # Implement writing to event file
    pass


def list_events_in_week(year, month, week):
    # Implement listing events in a week
    pass


def read_tags_file():
    with open("templates/tags.md", "r") as f:
        tags = yaml.safe_load(f)
    return tags


def write_tags_file(tag_data, append=False):
    if append:
        tags = read_tags_file()
        tags.append(tag_data)
    else:
        tags = [tag_data]

    with open("templates/tags.md", "w") as f:
        yaml.safe_dump(tags, f)


def read_people_file():
    # Implement reading people file
    pass


def write_people_file(person_data, append=False):
    if append:
        people = read_people_file()
        people.append(person_data)
    else:
        people = [person_data]

    with open("templates/people.md", "w") as f:
        yaml.safe_dump(people, f)


def read_bio_file():
    # Implement reading bio file
    pass


def write_bio_file(bio_data):
    # Implement writing to bio file
    pass


def read_personality_file():
    # Implement reading personality file
    pass


def write_personality_file(personality_data):
    # Implement writing to personality file
    pass
