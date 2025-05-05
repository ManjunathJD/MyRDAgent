"""
This is the preliminary version of the APE (Automated Prompt Engineering)
"""

from pathlib import Path

from rdagent.core.conf import RD_AGENT_SETTINGS


def get_llm_qa(file_path):
    data_flt = []
    with open(file_path, "rb") as f:
        data = f.read()
        print(len(data))
        for item in data: # type: ignore
            if "debug_llm" in item["tag"]:
                data_flt.append(item)
    return data_flt


# Example usage
# use
file_path = Path(RD_AGENT_SETTINGS.log_trace_path) / "debug_llm.pkl"
llm_qa = get_llm_qa(file_path)
print(len(llm_qa))

print(llm_qa[0])

# Initialize APE backend
from rdagent.oai.llm_utils import APIBackend
from rdagent.utils.agent.tpl import T

api = APIBackend()

# Analyze test data and generate improved prompts
for qa in llm_qa: # type: ignore
    # Generate system prompt for APE
    system_prompt = T(".prompts:ape.system").r()

    # Generate user prompt with context from LLM QA
    user_prompt = T(".prompts:ape.user").r(
        system=qa["obj"].get("system", ""), user=qa["obj"]["user"], answer=qa["obj"]["resp"] # type: ignore
    )
    analysis_result = api.build_messages_and_create_chat_completion(
        system_prompt=system_prompt, user_prompt=user_prompt
    )
    print(f"█" * 60)
    yes = input("Do you want to continue? (y/n)")
