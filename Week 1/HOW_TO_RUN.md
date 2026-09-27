# Week 1 — How to run

From the `Week 1` folder, with the virtual environment activated:

```
python skeleton\00_setup_check.py
python skeleton\01_assistant_vs_agent.py
python skeleton\02_llm_reasoning_limits.py
python skeleton\03_agent_anatomy.py
python skeleton\04_agent_loop.py
python skeleton\05_reflection_loop.py
python skeleton\06_multi_tool_agent.py
python skeleton\07_advanced_agent.py
```

Provider: Groq, model `openai/gpt-oss-120b` (set via `LLM_PROVIDER` / `LLM_MODEL` in `.env`).

| File | Expected result |
|------|-----------------|
| 00 | `[OK] Success!` |
| 01 | 823.8 (assistant and calculator agree) |
| 02 | Box puzzle: A Red, B Green, C empty, Pocket Blue |
| 03 | Example + my agent blueprint printed |
| 04 | `AGENT'S FINAL ANSWER: 180` |
| 05 | `reflection: CONFIRM` → `FINAL: 180` |
| 06 | `FINAL: 155` |
| 07 | 180 and $155, both confirmed |
