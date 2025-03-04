#!/usr/bin/env python3

import sys

from garak.attempt import Attempt
from garak.probes.base import Probe


hijacking_attacks = (
    "ignore-say ignore-print ignore-print-upper nevermind screaming-stop".split()
)
rogue_strings = "hate-humans kill-humans long-prompt".split()

this = sys.modules[__name__]


def constructor(self):
    super(self.__class__, self).__init__()
    from resources.promptinject import (
        build_prompts,
        prompt_data,
    )

    self.pi_prompt_data = prompt_data
    self.pi_build_prompts = build_prompts
    self.load_data_all_attacks()

    # self.prompts.append(f"{prefix} {false_assertion}")


def load_data_all_attacks(self):
    prompt_config = {
        "base": {
            "text": self.pi_prompt_data.ALL_OPENAI_PLAYGROUND_PROMPTS,
        },
        "attack": {
            "text": (
                self.pi_prompt_data.goal_hikacking_attacks["ignore-print"],
                self.pi_prompt_data.goal_hikacking_attacks["ignore-say"],
                self.pi_prompt_data.goal_hikacking_attacks["ignore-print-upper"],
                self.pi_prompt_data.goal_hikacking_attacks["nevermind"],
                self.pi_prompt_data.goal_hikacking_attacks["screaming-stop"],
            ),
            "rogue_string": self.pi_prompt_data.rogue_strings[self.rogue_string],
            "scoring": "match_rogue_to_output",
            "settings": {
                "escape": self.pi_prompt_data.escape_chars["n"],
                "delimiter": self.pi_prompt_data.delimiter_chars["dash"],
                "escape_length": 10,
                "escape_times": 2,
            },
        },
        "config": {
            "id": (0, 1, 2, 3),
        },
        "visualization": {"columns": ()},
    }
    self.prompts = []
    self.pi_prompts = self.pi_build_prompts(prompt_config)
    for pi_prompt in self.pi_prompts:
        self.prompts.append(pi_prompt["prompt"])


def _attempt_prestore_hook(self, attempt: Attempt, seq: int) -> Attempt:
    attempt.notes["settings"] = self.pi_prompts[seq]["settings"]
    attempt.notes["trigger"] = self.pi_prompts[seq]["settings"]["attack_rogue_string"]
    return attempt


def _generator_precall_hook(self, generator, attempt):
    map_attribs = (
        "temperature top_p frequency_penalty presence_penalty max_tokens".split()
    )
    for map_attrib in map_attribs:
        if map_attrib in dir(generator):
            setattr(
                generator,
                map_attrib,
                attempt.notes["settings"]["config_" + map_attrib],
            )


for rogue_string in rogue_strings:
    classname = "Hijack" + rogue_string.replace("-", " ").title().replace(" ", "")

    setattr(
        this,
        classname,
        type(
            classname,
            (Probe,),
            {
                "__init__": constructor,
                "name": "promptinject_" + rogue_string,
                "bcp47": "en",
                "description": "PromptInject is a framework that assembles prompts in a modular fashion to provide a quantitative analysis of the robustness of LLMs to adversarial prompt attacks. trophy Best Paper Awards @ NeurIPS ML Safety Workshop 2022",
                "recommended_detector": [
                    "promptinject.AttackRogueString",
                ],
                "load_data_all_attacks": load_data_all_attacks,
                "uri": "https://openreview.net/forum?id=qiaRo_7Zmug",
                "rogue_string": rogue_string,
                "_attempt_prestore_hook": _attempt_prestore_hook,
                "_generator_precall_hook": _generator_precall_hook,
            },
        ),
    )
