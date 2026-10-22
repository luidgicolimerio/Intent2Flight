from langchain_core.tools import StructuredTool
from pydantic import BaseModel
import asyncio
import glob
import os
from pathlib import Path

SKILLS_DIR = str(Path(__file__).resolve().parents[2] / "skills")


def load_skills() -> dict[str, dict]:
    skills = {}
    for md_path in glob.glob(f"{SKILLS_DIR}/**/*.md", recursive=True):
        content = open(md_path).read()
        name = desc = None
        for line in content.splitlines():
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("description:"):
                desc = line.split(":", 1)[1].strip()
        if name:
            script_path = os.path.join(os.path.dirname(md_path), f"{name.replace('-', '_')}.py")
            skills[name] = {"description": desc or name, "script_path": script_path}
    return skills


def build_skill_tool(api_url: str = "") -> StructuredTool:
    skills = load_skills()
    descriptions = "\n".join(f"- {n}: {v['description']}" for n, v in skills.items())
    porta_api = api_url.split(":")[-1] if api_url else "8000"

    class RunSkillInput(BaseModel):
        skill_name: str
        args: str = ""

    async def _run_skill(skill_name: str, args: str = "") -> str:
        skill = skills.get(skill_name)
        if not skill:
            return f"Skill '{skill_name}' não encontrada. Disponíveis: {list(skills.keys())}"
        script = skill["script_path"]
        if not os.path.exists(script):
            return f"Script não encontrado: {script}"
        base_args = f"--url localhost:{porta_api}"
        full_args = f"{base_args} {args}".strip()
        cmd = ["python", script] + full_args.split()
        print(f"[run_skill] Executando: python {script} {full_args}")
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=None, stderr=None)
        return f"Skill '{skill_name}' iniciada em background (PID {proc.pid})."

    return StructuredTool.from_function(
        coroutine=_run_skill,
        name="run_skill",
        description=(
            f"Executa um script de skill no drone em background (processo de longa duração).\n\n"
            f"Skills disponíveis:\n{descriptions}\n\n"
            f"  skill_name: Nome da skill (ex: 'gps-follower')\n"
            f"  args: Argumentos de linha de comando (ex: '--leader-url localhost:8001 --offset-north -5')"
        ),
        args_schema=RunSkillInput,
    )
