#!/usr/bin/env python3

from garak._config import args
from garak.detectors.base import HFDetector


class ToxicCommentModel(HFDetector):
    def __init__(self):
        self.name = "toxic-comment-model"
        super().__init__("martin-ha/toxic-comment-model", "toxic")
        self.description = (
            "Using martin-ha/toxic-comment-model DistilBERT to detect toxic content"
        )
        self.bcp47 = "en"
        self.tokenizer_kwargs = {"padding": True, "truncation": True, "max_length": 512}
