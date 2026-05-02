import dspy

# 2B sidekick drafts, 31B audits
sidekick_2b = dspy.LM(model="openai/gemma-4-2b-it", api_base="http://127.0.0.1:8080/v1")
heavy_31b = dspy.LM(model="openai/gemma-4-31b-it", api_base="http://127.0.0.1:8081/v1")
dspy.settings.configure(rm=None, lm=sidekick_2b)


class GEPARouter(dspy.Module):
    def __init__(self):
        super().__init__()
        self.draft = dspy.ChainOfThought("task -> initial_code_draft")
        self.audit = dspy.ChainOfThought("task, draft -> confidence_score, final_code_payload")

    def forward(self, task):
        with dspy.context(lm=sidekick_2b):
            fast_draft = self.draft(task=task)
        with dspy.context(lm=heavy_31b):
            final = self.audit(task=task, draft=fast_draft.initial_code_draft)
        return final
