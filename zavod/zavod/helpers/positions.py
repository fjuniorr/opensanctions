from banal import ensure_list
from typing import Optional, Iterable, List

from zavod.context import Context
from zavod.entity import Entity
from zavod import settings


AFTER_OFFICE = 5 * 365


def make_position(
    context: Context,
    name: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    country: Optional[str | Iterable[str]] = None,
    subnational_area: Optional[str] = None,
    organization: Optional[Entity] = None,
    inception_date: Optional[Iterable[str]] = None,
    dissolution_date: Optional[Iterable[str]] = None,
    number_of_seats: Optional[str] = None,
    wikidata_id: Optional[str] = None,
    source_url: Optional[str] = None,
    lang: Optional[str] = None,
) -> Entity:
    """Create consistent position entities. Help make sure the same position
    from different sources will end up with the same id, while different positions
    don't end up overriding each other.

    Args:
        context: The context to create the entity in.
        name: The name of the position.
        summary: A short summary of the position.
        description: A longer description of the position.
        country: The country or countries the position is in.
        subnational_area: The state or district the position is in.
        organization: The organization the position is a part of.
        inception_date: The date the position was created.
        dissolution_date: The date the position was dissolved.
        number_of_seats: The number of seats that can hold the position.
        wikidata_id: The Wikidata QID of the position.
        source_url: The URL of the source the position was found in.
        lang: The language of the position details.

    Returns:
        A new entity of type `Position`."""

    position = context.make("Position")

    position.add("name", name, lang=lang)
    position.add("summary", summary, lang=lang)
    position.add("description", description, lang=lang)
    position.add("country", country, lang=lang)
    position.add("organization", organization, lang=lang)
    position.add("subnationalArea", subnational_area, lang=lang)
    position.add("inceptionDate", inception_date)
    position.add("dissolutionDate", dissolution_date)
    position.add("numberOfSeats", number_of_seats)
    position.add("wikidataId", wikidata_id)
    position.add("sourceUrl", source_url)

    parts: List[str] = [name]
    if country is not None:
        parts.extend(ensure_list(country))
    if inception_date is not None:
        parts.extend(ensure_list(inception_date))
    if dissolution_date is not None:
        parts.extend(ensure_list(dissolution_date))

    if wikidata_id is not None:
        position.id = wikidata_id
    else:
        position.id = context.make_id(*parts)

    return position


def make_occupancy(
    context: Context,
    person: Entity,
    position: Entity,
    no_end_implies_current: bool,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Optional[Entity]:
    """Make occupancies if they meet our criteria for PEP position occupancy"""
    if end_date is None or end_date > h.backdate(settings.RUN_TIME, AFTER_OFFICE):
        occupancy = context.make("Occupancy")
        parts = [person.id, position.id, start_date, end_date]
        occupancy.id = context.make_id(*parts)
        occupancy.add("holder", person)
        occupancy.add("post", position)
        occupancy.add("startDate", start_date)
        if end_date:
            occupancy.add("endDate", end_date)
        if no_end_implies_current and not end_date:
            status = "Current"
        else:
            status = "Ended"
        occupancy.add("status", status)
        return occupancy
    return None