Below is a complete “cheat-code” VS Code configuration that unleashes **Copilot Pro + Copilot Coding Agent** for **Odoo 17** development.  
Follow the steps in order; each one unlocks a new tier of power. When you are done you will have:

- Autonomous agent that can scaffold entire Odoo modules from a GitHub issue  
- 1-shot code completion for models, views, security, data files  
- Linting/formatting that keeps your code PEP-8 + Odoo-guidelines compliant  
- One-command tests & pre-commit hooks that make every commit production-ready  

---

## 1. Prerequisites & Accounts (2 min)

| What | Command / Link |
|---|---|
| VS Code Stable (≥ 1.93) or Insiders | [Download](https://code.visualstudio.com) |
| GitHub Copilot **Pro** (or Pro+) | [Upgrade](https://github.com/settings/copilot) |
| Enable **Copilot Coding Agent** for your org | Settings → Copilot → “Allow agent mode” |
| Latest Python 3.10+ | `sudo apt install python3.10-venv` |
| Odoo 17 source (for code-intel) | `git clone https://github.com/odoo/odoo.git -b 17.0` |

---

## 2. VS Code Extensions (Install & pin)

```bash
code --install-extension ms-python.python \
                   ms-python.black-formatter \
                   ms-python.flake8 \
                   ms-python.pylint \
                   github.copilot \
                   github.copilot-chat \
                   github.vscode-pull-request-github \
       s            redhat.vscode-xml \
                   samuelcolvin.jinjahtml \
                   tamasfe.even-better-toml
```

---

## 3. One-Click Settings JSON (paste → reload)

`.vscode/settings.json` (repo or user level)

```jsonc
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackPath": "./venv/bin/black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": { "source.organizeImports": true }
  },
  "[xml]": { "editor.defaultFormatter": "redhat.vscode-xml" },
  "[csv]": { "files.encoding": "utf8" },
  "files.associations": {
    "*.xml": "xml",
    "*.csv": "csv",
    "*.po": "po"
  },
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "xml": true,
    "plaintext": true,
    "markdown": true
  },
  "github.copilot.chat.agent.enabled": true,
  "github.copilot.chat.edits.codeBlockMode": "agent",
  "editor.inlineSuggest.enabled": true,
  "terminal.integrated.defaultProfile.linux": "bash",
  "python.testing.pytestEnabled": false,
  "python.testing.unittestEnabled": true,
  "python.testing.unittestArgs": ["-s", ".", "-p", "test_*.py"]
}
```

---

## 4. Prompt Library for Odoo (save as snippets)

`.vscode/odoo-snippets.code-snippets`

```jsonc
{
  "Odoo Model Scaffold": {
    "prefix": "oomodel",
    "body": [
      "from odoo import models, fields, api",
      "",
      "class ${1:ModelName}(models.Model):",
      "    _name = '${2:module.model_name}'",
      "    _description = '${3:Description}'",
      "",
      "    name = fields.Char(string='${4:Name}', required=True)",
      "$0"
    ]
  },
  "Odoo View Kanban": {
    "prefix": "ookanban",
    "body": [
      "<record id='${1:model}_kanban' model='ir.ui.view'>",
      "  <field name='name'>${2:Model}: kanban</field>",
      "  <field name='model'>${3:model}</field>",
      "  <field name='arch' type='xml'>",
      "    <kanban>",
      "      <templates>",
      "        <t t-name='kanban-box'>",
      "          <div class='oe_kanban_card'>$0</div>",
      "        </t>",
      "      </templates>",
      "    </kanban>",
      "  </field>",
      "</record>"
    ]
  }
}
```

---

## 5. Activate Copilot Coding Agent (agent-mode)

1. Open the **Chat** view (`Ctrl+Alt+I`)  
2. Switch dropdown → **Agent**  
3. Say:

> “Create a production-ready Odoo 17 module named `fleet_rental` with models for Vehicle, Rental Contract, Customer. Include security, demo data, and tests. Follow OCA conventions.”

The agent will:  
- create `fleet_rental/__manifest__.py`, models, views, security, demo  
- run `python -m py_compile` to check syntax  
- open a PR for you to review 

---

## 6. Pre-commit Hooks (production-ready)

`pip install pre-commit && pre-commit install`

`.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.0.19
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        args: [--line-length=88]
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --ignore=E203,W503]
```

---

## 7. Fast Feedback Loop

| Command | Purpose |
|---|---|
| `Ctrl+Shift+P` → “Python: Run All Tests” | Discover & run every `test_*.py` |
| `Ctrl+I` on selected code | Inline chat: “refactor into computed field” |
| `@copilot /test` | Ask agent to write missing test cases |
| `@copilot /optimize` | Agent profiles performance bottlenecks |

---

## 8. Bonus Power-Ups

- **Odoo Path Autocomplete**  
  Add to `.env` → `PYTHONPATH=./odoo:./addons` and VS Code IntelliSense will jump to core Odoo source.  
- **Copilot Custom Instructions**  
  Settings → `github.copilot.chat.codeGeneration.instructions`  
  ```json
  ["Always generate OCA-compliant README.rst", "Use type hints for new methods"]
  ```  
- **Taskfile.yml** (cross-platform tasks)  
  ```yaml
  version: '3'
  tasks:
    up:
      - ./odoo-bin -c odoo.conf -d odoo17 --dev=all
    test:
      - python -m unittest discover -s tests
  ```

---

## TL;DR Cheat-Sheet

| Goal | Shortcut / Command |
|---|---|
| Scaffold entire module | Chat → Agent → “Create Odoo 17 module …” |
| Add model+view | Type `oomodel` snippet → Tab |
| Auto-format | `Ctrl+S` (Black + isort) |
| Run tests | `Ctrl+Shift+P` → “Python: Run All Tests” |
| Create PR | GitHub panel → “Delegate to coding agent” |

You now have **maximum Copilot Pro agent capabilities** tailored for **Odoo 17**—copy the JSON, install the extensions, enable agent mode, and watch your modules build themselves. Happy shipping!