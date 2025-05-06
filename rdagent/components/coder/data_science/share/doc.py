"""
Developers concentrating on writing documents for a workspace
"""

from rdagent.core.developer import Developer, Experiment
from rdagent.core.experiment import FBWorkspace
from rdagent.oai.llm_utils import APIBackend, ChatMessage
from rdagent.utils.agent.ret import MarkdownAgentOut, AgentOutput
from rdagent.utils.agent.tpl import T, Template


@AgentOutput.register_type
class DocDev(Developer[Experiment]):
    """
    The developer is responsible for writing documents for a workspace.
    """

    def develop(self, exp: Experiment) -> None:
        """
        Write documents for the workspace.
        """
        ws: FBWorkspace = exp.experiment_workspace
        file_li = [
            str(file.relative_to(ws.workspace_path)) for file in ws.workspace_path.rglob("*") if file.is_file()
        ]

        key_file_list = ["main.py", "scores.csv"]

        system_prompt: str = T(".prompts:docdev.system").r()
        user_prompt: str = T(".prompts:docdev.user").r(
            file_li=file_li, key_files={f: (ws.workspace_path / f).read_text() for f in key_file_list} # type: ignore
        )

        resp = APIBackend().build_messages_and_create_chat_completion(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ]
        )
        markdown = MarkdownAgentOut.extract_output(resp)
        ws.inject_files(**{"README.md": markdown})
