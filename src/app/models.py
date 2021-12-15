from typing import Optional, List, Dict, Text
from pydantic import BaseModel
from pydantic.types import OptionalInt


class NotationTexts(BaseModel):
    en: Optional[Text]
    de: Optional[Text]
    fr: Optional[Text]
    it: Optional[Text]
    pt: Optional[Text]
    fi: Optional[Text]
    pl: Optional[Text]
    jp: Optional[Text]
    zh: Optional[Text]
    nl: Optional[Text]
    es: Optional[Text]


class KeywordTexts(BaseModel):
    en: Optional[List[Text]]
    de: Optional[List[Text]]
    fr: Optional[List[Text]]
    it: Optional[List[Text]]
    pt: Optional[List[Text]]
    fi: Optional[List[Text]]
    pl: Optional[List[Text]]
    jp: Optional[List[Text]]
    zh: Optional[List[Text]]
    nl: Optional[List[Text]]
    es: Optional[List[Text]]


class Notation(BaseModel):
    n: Text
    p: List[Text]
    c: Optional[List[Text]]
    r: Optional[List[Text]]
    txt: NotationTexts
    kw: Optional[KeywordTexts]


class FilledNotation(BaseModel):
    n: Text
    p: List[Dict]
    c: Optional[List[Dict]]
    r: Optional[List[Dict]]
    txt: NotationTexts
    kw: Optional[KeywordTexts]
    image_count: OptionalInt


class JSKOS(BaseModel):
    uri: Text
    type: List[Text]
    notation: List[Text]
    prefLabel: Optional[Dict]
    altLabel: Optional[Dict]
    ancestors: Optional[List]
    narrower: Optional[List]
    related: Optional[List]


class JSONLD(BaseModel):
    graph: List[Dict]
