"""Why something is unknown, and what kind of completeness was actually achieved.

Two vocabularies that were previously collapsed, each collapse having produced a
measured failure.

**Causes of UNKNOWN.** A single UNKNOWN cannot be acted on. "I have no evidence"
and "two adapters disagree" and "my decoder cannot read this format" call for
three different next steps -- ask, adjudicate, write an adapter -- and a caller
that sees only UNKNOWN takes none of them. The causes are kept internally and
may collapse to a bare UNKNOWN at the boundary.

**Levels of completeness.** The previous version had one boolean, and it lied.
During the scan that found zero XMP packets in 1372 QuickTime files, every one
of those files was flagged ``exhaustive`` -- true, because the walker had visited
every node of the tree it knew how to traverse, and useless, because it was
looking for Adobe's ``uuid`` box in a container that stores the packet in an
atom named ``XMP_``. The flag described an intention to traverse, not coverage.

So completeness is five separate questions and NONE implies the next:

    traversal   did the walker visit every node of the structure it traverses?
    vocabulary  is the set of packet-bearing containers it knows complete for
                this format?                                  <- FALSE for .mov
    authority   did the authority reach every member of the group?
    corpus      is the corpus itself complete over the domain of the question?
    semantic    does absence of the evidence imply absence of the fact?

The .mov failure lived entirely in the gap between the first and the second, and
there was no field able to express it. That is why this module exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONTRACT = "mak-epistemics-v1"

# --------------------------------------------------------- causes of UNKNOWN

MISSING_EVIDENCE = "MISSING_EVIDENCE"
"""No evidence was found. The next step is to look somewhere else, or to ask."""

INCOMPLETE_AUTHORITY = "INCOMPLETE_AUTHORITY"
"""Evidence exists but the authority did not cover every member. Extend coverage."""

OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
"""The question does not apply to this object. Not a gap; a category error."""

DECODER_LIMIT = "DECODER_LIMIT"
"""This layer cannot read the format or the container. Write an adapter."""

CONFLICT = "CONFLICT"
"""Two pieces of evidence disagree. Adjudicate; never average."""

INVALID_QUERY = "INVALID_QUERY"
"""The question is malformed for this vocabulary. Fix the question."""

UNKNOWN_CAUSES = (MISSING_EVIDENCE, INCOMPLETE_AUTHORITY, OUT_OF_DOMAIN,
                  DECODER_LIMIT, CONFLICT, INVALID_QUERY)

# What a caller should do next. Kept beside the cause because a cause whose
# remedy is unstated tends to be treated as a dead end.
REMEDY = {
    MISSING_EVIDENCE: "look elsewhere, or ask the operator",
    INCOMPLETE_AUTHORITY: "extend the authority's coverage over the group",
    OUT_OF_DOMAIN: "nothing: the question does not apply here",
    DECODER_LIMIT: "write or fix an adapter for this format",
    CONFLICT: "adjudicate between the disagreeing sources",
    INVALID_QUERY: "restate the question in the declared vocabulary",
}

# ------------------------------------------------------- completeness levels

TRAVERSAL = "traversal"
VOCABULARY = "vocabulary"
AUTHORITY = "authority"
CORPUS = "corpus"
SEMANTIC = "semantic"

COMPLETENESS_LEVELS = (TRAVERSAL, VOCABULARY, AUTHORITY, CORPUS, SEMANTIC)

LEVEL_MEANING = {
    TRAVERSAL: "every node of the structure this walker traverses was visited",
    VOCABULARY: "the set of packet-bearing containers this walker knows is "
                "complete for the format",
    AUTHORITY: "the authority produced evidence for every member of the group",
    CORPUS: "the corpus is complete over the domain of the question",
    SEMANTIC: "absence of this evidence implies absence of the fact",
}

# A level may be asserted, denied, or simply not assessed. The third is the
# honest default and the one the old boolean could not express.
YES = "yes"
NO = "no"
UNASSESSED = "unassessed"
VERDICTS = (YES, NO, UNASSESSED)


class EpistemicError(ValueError):
    """A completeness claim or an UNKNOWN cause was stated outside the vocabulary."""


@dataclass(frozen=True)
class Completeness:
    """Five independent verdicts. None of them implies another."""

    traversal: str = UNASSESSED
    vocabulary: str = UNASSESSED
    authority: str = UNASSESSED
    corpus: str = UNASSESSED
    semantic: str = NO           # default NO: tools strip metadata, so absence of
                                 # evidence never implies absence of the fact.
    note: str = ""

    def __post_init__(self) -> None:
        for level in COMPLETENESS_LEVELS:
            value = getattr(self, level)
            if value not in VERDICTS:
                raise EpistemicError(f"bad_{level}_verdict: {value}")

    @property
    def negative_is_evidence(self) -> bool:
        """A miss means something only when traversal AND vocabulary both hold.

        Semantic completeness would be needed to go further, and it is never
        available for embedded metadata, so this stops at the decoder's claim:
        "no packet exists in this file under a complete vocabulary" -- which is
        NOT "this file has no provenance".
        """
        return self.traversal == YES and self.vocabulary == YES

    @property
    def strongest_negative_claim(self) -> str:
        """The exact sentence a negative from this search is allowed to be."""
        if self.traversal != YES:
            return "nothing: the structure was not fully traversed"
        if self.vocabulary != YES:
            return ("nothing: the walker's container vocabulary is not known to be "
                    "complete for this format, which is exactly the .mov failure")
        if self.semantic == YES:
            return "the fact is absent"
        return ("no evidence of this kind exists in this object, under this "
                "decoder version. NOT that the fact is absent.")

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract": CONTRACT,
            "traversal": self.traversal,
            "vocabulary": self.vocabulary,
            "authority": self.authority,
            "corpus": self.corpus,
            "semantic": self.semantic,
            "negative_is_evidence": self.negative_is_evidence,
            "strongest_negative_claim": self.strongest_negative_claim,
            "note": self.note,
        }


@dataclass(frozen=True)
class Unknown:
    """An UNKNOWN with its cause kept, and its remedy stated."""

    cause: str
    detail: str = ""
    completeness: Completeness | None = None

    def __post_init__(self) -> None:
        if self.cause not in UNKNOWN_CAUSES:
            raise EpistemicError(f"undeclared_unknown_cause: {self.cause}")

    @property
    def remedy(self) -> str:
        return REMEDY[self.cause]

    def outward(self) -> str:
        """What a consumer outside this layer sees. The cause stays inside."""
        return "UNKNOWN"

    def as_dict(self) -> dict[str, Any]:
        out = {
            "contract": CONTRACT,
            "verdict": "UNKNOWN",
            "cause": self.cause,
            "remedy": self.remedy,
            "detail": self.detail,
        }
        if self.completeness is not None:
            out["completeness"] = self.completeness.as_dict()
        return out


# The vocabulary a walker declares for a format. Kept as data so a gap is
# visible rather than implicit in code, which is what hid the .mov failure.
KNOWN_CONTAINERS: dict[str, dict[str, Any]] = {
    "png": {
        "containers": ["iTXt chunk keyed XML:com.adobe.xmp, deflated or plain"],
        "vocabulary_complete": YES,
        "why": "The PNG specification defines exactly one place for XMP.",
    },
    "jpeg": {
        "containers": ["APP1 with the Adobe XAP header",
                       "APP1 with the Extended XMP header"],
        "vocabulary_complete": YES,
        "why": "XMP part 3 defines these two for JPEG.",
    },
    "isobmff": {
        "containers": ["uuid box with Adobe's registered UUID (MP4)",
                       "XMP_ atom inside moov/udta (QuickTime)"],
        "vocabulary_complete": YES,
        "why": "Both were required in practice. The QuickTime atom was MISSING "
               "in the first version and produced 0 hits in 1372 real .mov files "
               "while a crude window scan found 180. It is listed here so the "
               "next gap of this kind is visible as data rather than as silence.",
    },
    "generic": {
        "containers": ["a raw <?xpacket ... ?> or <x:xmpmeta> region"],
        "vocabulary_complete": NO,
        "why": "A packet may be stored in a format-specific structure this "
               "fallback cannot name. TIFF tag 700 and PDF metadata streams are "
               "two known cases that are found only by luck here.",
    },
}
