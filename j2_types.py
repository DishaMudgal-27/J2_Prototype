"""BuilderReply: the reply model for a work atom's builder (Pydantic 2), behind J2_TEMPLATES=1.

The field names are the ones a builder's JSON line already uses today (j2.J2Run._turn_workflow_agent and
_doc_prompt): reason, say, human_output, atom_human_output, next, and the optional question / board_used
(J2_BOARD=1) and spec_conflict (an LLD slice). Nothing is renamed and nothing is added: the model only writes down
the shape those prompts already ask for, so a reply can be checked instead of hoped for. The fenced blocks that
follow the JSON line (```section, ```head, ```markdown, ```style) are not part of this model; parse_section,
parse_doc and parse_style read them as they always did.

format_for() builds both the reply-format line for the prompt and the JSON Schema for its <reply_schema> tag from
the model itself, so the two can never drift apart. Python 3.9: Optional/Union, never "X | None".
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

MODEL = "BuilderReply/1"
# The fields each builder is asked for, in the order the prompt lists them. A website builder with an LLD slice also
# gets spec_conflict, and with J2_BOARD=1 every builder gets question and board_used (see j2.J2Run.BOARD_FMT).
BASE_FIELDS = ("reason", "say", "human_output", "atom_human_output", "next")
BOARD_FIELDS = ("question", "board_used")
SPEC_FIELDS = ("spec_conflict",)


class BoardQuestion(BaseModel):
    """question: the one atom that knows, what it is about, and the question itself (j2.J2Run.BOARD_FMT)."""
    model_config = ConfigDict(extra="allow")

    to: str = Field(description="an atom id from OTHER SECTIONS or BOARD: the one atom that knows")
    about: Optional[str] = Field(default=None, description="what the question is about")
    text: str = Field(description="the question itself")


class SpecConflict(BaseModel):
    """spec_conflict: an LLD slice that can't be built as written (j2.J2Run.SPEC_FMT)."""
    model_config = ConfigDict(extra="allow")

    section: str = Field(description="the LLD section id")
    reason: Optional[str] = Field(default=None, description="why it can't be built as written")
    use: Optional[Dict[str, str]] = Field(default=None, description='{"#spec-selector": "#selector-you-built"}')
    fields: Optional[Dict[str, Optional[str]]] = Field(
        default=None, description='{"F4": null|"text"}: null removes that spec field, a string gives its new type')


class BuilderReply(BaseModel):
    """The JSON object on the first line of a builder's reply. Extra keys are kept, never rejected: the model proves
    the fields the prompt asked for are there and well typed, and says nothing about anything else."""
    model_config = ConfigDict(extra="allow")

    reason: str = Field(description="one short sentence: why you decided this")
    say: str = Field(min_length=1, description="one short line reporting to @Coordination: what you changed; code "
                                               "runs your checks and reports them, so don't claim they pass")
    human_output: str = Field(min_length=1, description="1 to 3 plain sentences telling a person what you built; "
                                                        '"done." alone is rejected')
    atom_human_output: str = Field(min_length=1, description="1 or 2 plain sentences telling the Requester what this "
                                                             "part created, in everyday words: no ids, no selectors, "
                                                             'no "units"')
    next: str = Field(description='"Coordination"')
    question: Optional[BoardQuestion] = Field(default=None, description="optional: at most one question per atom, "
                                                                        "never one already answered")
    board_used: Optional[List[str]] = Field(default=None, description='optional: the board ids, e.g. ["Q-1"], whose '
                                                                      "answer you used")
    spec_conflict: Optional[SpecConflict] = Field(default=None, description="only when your spec can't be built as "
                                                                           "written; never deviate silently")


MODELS = {MODEL: BuilderReply}


def _type_text(name, field):
    """A field's type as the prompt words it: str, [str], the nested object's own shape, or null|<shape>."""
    ann = field.annotation
    inner = {"question": '{"to": str, "about": str, "text": str}',
             "board_used": "[str]",
             "spec_conflict": '{"section": str, "reason": str, "use": {"#spec-selector": "#selector"}, '
                              '"fields": {"F4": null|"text"}}'}.get(name)
    if inner:
        return f"null|{inner}"
    return "str" if ann is str else getattr(ann, "__name__", str(ann))


def format_for(model=BuilderReply, fields=None):
    """(reply-format text, JSON Schema) for a reply model: the line the prompt asks for and the schema its
    <reply_schema> tag carries. fields limits it to the ones this builder is asked for (BASE_FIELDS, plus the board's
    and the slice's when they apply), in the model's own order, so the prompt and the schema always agree."""
    want = [f for f in (fields or list(model.model_fields)) if f in model.model_fields]
    parts = []
    for name in want:
        f = model.model_fields[name]
        parts.append(f'"{name}": {_type_text(name, f)} ({f.description})' if f.description
                     else f'"{name}": {_type_text(name, f)}')
    schema = model.model_json_schema()
    schema = {**schema, "properties": {k: v for k, v in (schema.get("properties") or {}).items() if k in want},
              "required": [k for k in (schema.get("required") or []) if k in want]}
    return "{" + ", ".join(parts) + "}", schema


def validate(text, model=BuilderReply):
    """(reply or None, [error lines]) for the JSON line of a builder's reply, read by Pydantic. The errors are the
    exact ones Pydantic reports ("next: Field required"), so the retry can quote them to the builder."""
    try:
        return model.model_validate_json(text), []
    except Exception as e:
        return None, errors_of(e)


def errors_of(e):
    """Pydantic's errors as one line each: "<field>: <message>"."""
    out = []
    for err in getattr(e, "errors", lambda: [])() or []:
        where = ".".join(str(x) for x in err.get("loc") or ()) or "reply"
        out.append(f"{where}: {err.get('msg')}")
    return out or [str(e).splitlines()[0]]
