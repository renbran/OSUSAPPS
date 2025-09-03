{
  // ====== GITHUB COPILOT CONFIGURATION ======
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": true,
    "markdown": true,
    "python": true,
    "xml": true,
    "javascript": true,
    "css": true,
    "sql": true,
    "json": true
  },
  
  // Copilot Chat Settings
  "github.copilot.chat.enabled": true,
  "github.copilot.chat.welcomeMessage": "always",
  "github.copilot.chat.localeOverride": "en",
  
  // Enhanced Copilot Features
  "github.copilot.advanced": {
    "secret_key": "default",
    "length": 500,
    "temperature": 0.1,
    "top_p": 1,
    "inlineSuggestCount": 3,
    "listCount": 10,
    "debug": false
  },
  
  // ====== ENHANCED COPILOT INSTRUCTIONS WITH SPEC WORKFLOW ======
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "@spec-workflow Rule - Spec Process: Before any major feature development, ALWAYS follow the spec workflow: 1) Create EARS requirements document (.claude/specs/{feature_name}/requirements.md), 2) Create design document (.claude/specs/{feature_name}/design.md), 3) Then implement. Use EARS format (WHEN/IF/WHERE/WHILE + SHALL) for requirements."
    },
    {
      "text": "@spec-requirements Rule - EARS Format: When writing requirements, use Easy Approach to Requirements Syntax (EARS). Format: 'WHEN [event] THEN [system] SHALL [response]' or 'IF [precondition] THEN [system] SHALL [response]'. Each requirement must have user story format: 'As a [role], I want [feature], so that [benefit]'."
    },
    {
      "text": "@spec-design Rule - Design Documentation: Design documents must include: Overview, System Architecture Diagram (Mermaid), Data Flow Diagram (Mermaid), Component Design with interfaces, Data Models (TypeScript interfaces), Business Process (Mermaid flowcharts), Error Handling Strategy, Testing Strategy."
    },
    {
      "text": "@spec-validation Rule - Approval Process: Never proceed to implementation without explicit approval of requirements and design documents. Always ask 'Do the requirements look good? If so, we can move on to the design.' and 'Does the design look good? If so, we can move on to implementation.'"
    },
    {
      "text": "@odoo17 Rule - Odoo 17 Architecture: Always follow Odoo 17 MVC architecture patterns. Use proper model inheritance (models.Model, models.TransientModel, models.AbstractModel), ensure proper field definitions with appropriate attributes, and implement computed fields with @api.depends decorators."
    },
    {
      "text": "@odoo17 Rule - Security & Access Control: Implement proper security groups, access rights (ir.model.access.csv), and record rules (ir.rule). Always use sudo() carefully and validate user permissions. Follow the principle of least privilege."
    },
    {
      "text": "@odoo17 Rule - Data Integrity: Use proper field constraints, ondelete cascading, and database indexing. Implement _sql_constraints for database-level validation and @api.constrains for Python-level validation."
    },
    {
      "text": "@odoo17 Rule - Performance Optimization: Use proper ORM methods (search_read, read_group), avoid N+1 queries, implement proper lazy loading, and use batch operations. Always consider database impact and use prefetch when needed."
    },
    {
      "text": "@odoo17 Rule - Module Structure: Follow Odoo 17 module structure with proper __manifest__.py, organized file structure (models/, views/, data/, static/, etc.), and appropriate dependencies declaration."
    },
    {
      "text": "@odoo17 Rule - XML/QWeb Standards: Use proper XML structure, semantic field groupings, appropriate view inheritance, and responsive design principles. Follow Odoo's UI/UX guidelines and accessibility standards."
    },
    {
      "text": "@odoo17 Rule - Python Code Quality: Follow PEP 8 standards, use proper docstrings, implement error handling with appropriate exceptions, and maintain backward compatibility when possible."
    },
    {
      "text": "@odoo17 Rule - API Design: Implement proper API endpoints with @http.route decorators, use appropriate authentication methods, implement proper JSON responses, and follow REST principles."
    },
    {
      "text": "@odoo17 Rule - Testing: Generate unit tests for models, integration tests for workflows, and functional tests for user interactions. Use Odoo's testing framework and maintain high code coverage."
    },
    {
      "text": "@documentation Rule - Comprehensive Documentation: Write detailed docstrings for all methods explaining purpose, arguments, return values, and examples. Include inline comments for complex logic. Maintain project documentation with architecture decisions."
    },
    {
      "text": "@workflow Rule - Development Workflow: Follow structured development: Spec → Requirements → Design → Implementation → Testing → Documentation. Never skip phases. Each phase requires explicit approval before proceeding."
    }
  ],
  
  // ====== ENHANCED REVIEW INSTRUCTIONS ======
  "github.copilot.chat.reviewSelection.instructions": [
    {
      "text": "# Comprehensive Code Review Checklist\n\n## Spec Workflow Compliance\n- [ ] Requirements document exists and follows EARS format\n- [ ] Design document exists with all required sections\n- [ ] Implementation matches approved design\n- [ ] All requirements are addressed in implementation\n- [ ] User stories are traceable to code\n\n## EARS Requirements Validation\n- [ ] All requirements use proper EARS syntax (WHEN/IF/WHERE/WHILE + SHALL)\n- [ ] Requirements are testable and measurable\n- [ ] User stories follow 'As a [role], I want [feature], so that [benefit]' format\n- [ ] Acceptance criteria are specific and actionable\n\n## Architecture & Design Review\n- [ ] Follows Odoo 17 MVC pattern correctly\n- [ ] Proper model inheritance usage\n- [ ] Appropriate field types and attributes\n- [ ] Correct use of computed fields with @api.depends\n- [ ] Design diagrams match implementation\n- [ ] Component interfaces are properly defined\n\n## Security Review\n- [ ] Security groups properly defined\n- [ ] Access rights (ir.model.access.csv) implemented\n- [ ] Record rules (ir.rule) when needed\n- [ ] Proper sudo() usage and security validation\n- [ ] Input sanitization and XSS prevention\n\n## Performance Analysis\n- [ ] Efficient database queries (no N+1 problems)\n- [ ] Proper use of search_read and read_group\n- [ ] Appropriate indexing on frequently queried fields\n- [ ] Batch operations for bulk data processing\n- [ ] Memory usage optimization\n\n## Code Quality\n- [ ] PEP 8 compliance\n- [ ] Proper error handling and logging\n- [ ] Comprehensive docstrings\n- [ ] Unit test coverage\n- [ ] No code duplication\n- [ ] Error handling strategy implemented\n\n## Odoo Standards\n- [ ] Proper module structure and organization\n- [ ] Correct __manifest__.py configuration\n- [ ] Appropriate view inheritance patterns\n- [ ] Translation support (_() function usage)\n- [ ] Proper field constraints and validations\n\n## Data Integrity\n- [ ] Database constraints implementation\n- [ ] Proper ondelete cascade relationships\n- [ ] Data migration scripts when needed\n- [ ] Backup and recovery considerations\n\n## Testing Strategy\n- [ ] Unit tests for models implemented\n- [ ] Integration tests for workflows created\n- [ ] Functional tests for user interactions\n- [ ] Test coverage meets requirements\n- [ ] Tests validate EARS requirements\n\n## Documentation Completeness\n- [ ] Comprehensive docstrings present\n- [ ] Architecture decisions documented\n- [ ] API documentation current\n- [ ] User documentation updated\n- [ ] Change log maintained"
    }
  ],
  
  // ====== SPEC WORKFLOW CHAT PARTICIPANTS ======
  "github.copilot.chat.participants": [
    {
      "id": "spec",
      "name": "Spec Workflow Expert",
      "description": "Specialized in EARS requirements and design documentation workflow",
      "commands": [
        "requirements", "design", "ears", "workflow", "validate", "approve"
      ]
    },
    {
      "id": "odoo",
      "name": "Odoo Expert", 
      "description": "Specialized in Odoo 17 development, architecture, and best practices",
      "commands": [
        "model", "view", "security", "workflow", "performance", "migration"
      ]
    },
    {
      "id": "requirements",
      "name": "Requirements Analyst",
      "description": "Expert in EARS format requirements creation and validation",
      "commands": [
        "ears", "user-story", "acceptance", "validate", "refine"
      ]
    },
    {
      "id": "design",
      "name": "Design Architect",
      "description": "Expert in system design, architecture diagrams, and technical specifications",
      "commands": [
        "architecture", "diagram", "component", "interface", "dataflow"
      ]
    }
  ],
  
  // ====== SPEC WORKFLOW COMMANDS ======
  "github.copilot.chat.commands": [
    {
      "name": "spec-start",
      "description": "Start the spec workflow process for a new feature",
      "template": "Start spec workflow for feature: ${feature_name}. Create requirements document in EARS format."
    },
    {
      "name": "spec-requirements", 
      "description": "Create or refine EARS requirements document",
      "template": "Create EARS requirements for ${feature_name}: ${feature_description}"
    },
    {
      "name": "spec-design",
      "description": "Create design document from approved requirements",
      "template": "Create design document for ${feature_name} based on approved requirements"
    },
    {
      "name": "spec-validate",
      "description": "Validate spec documents against standards",
      "template": "Validate requirements and design documents for completeness and standards compliance"
    },
    {
      "name": "odoo-module",
      "description": "Create complete Odoo module from approved spec",
      "template": "Generate Odoo 17 module for ${feature_name} following approved design"
    }
  ],
  
  // ====== EDITOR SETTINGS FOR COPILOT ======
  "editor.inlineSuggest.enabled": true,
  "editor.inlineSuggest.showToolbar": "always",
  "editor.suggestSelection": "first",
  "editor.tabCompletion": "on",
  "editor.wordBasedSuggestions": "matchingDocuments",
  "editor.semanticHighlighting.enabled": true,
  "editor.linkedEditing": true,
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": true,
  "editor.rulers": [88, 120],
  "editor.insertSpaces": true,
  "editor.tabSize": 4,
  "editor.detectIndentation": false,
  "editor.trimAutoWhitespace": true,
  "editor.formatOnSave": true,
  "editor.formatOnSaveMode": [
    "source.organizeImports",
    "source.fixAll",
    "source.format"
  ],
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit"
  },
  
  // ====== PYTHON CONFIGURATION ======
  "python.analysis.typeCheckingMode": "strict",
  "python.analysis.typeEvaluation.strictParameterNoneValue": false,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "python.formatting.autopep8Args": ["--select=E,W,F"],
  "python.defaultInterpreterPath": "./venv/bin/python",
  
  // ====== WORKBENCH SETTINGS ======
  "workbench.editor.enablePreview": false,
  "workbench.panel.showLabels": false,
  "workbench.secondarySideBar.defaultVisibility": "hidden",
  "workbench.settings.applyToAllProfiles": ["github.copilot.enable"],
  
  // ====== TERMINAL SETTINGS ======
  "terminal.integrated.defaultProfile.linux": "bash",
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.cursorBlinking": true,
  "terminal.integrated.shellIntegration.strongTypeSymbols": false,
  "terminal.integrated.shellAdapting.enableVCS": true,
  
  // ====== FILE MANAGEMENT ======
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 2500,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/filestore": true,
    "**/sessions": true,
    "**/.pytest_cache": true,
    "**/node_modules": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/filestore": true
  },
  
  // ====== SPEC WORKFLOW FILE ASSOCIATIONS ======
  "files.associations": {
    "requirements*.md": "markdown",
    "design*.md": "markdown",
    "*.ears": "markdown"
  },
  
  // ====== GIT CONFIGURATION ======
  "git.autofetch": true,
  "git.ignoreRebaseWarning": true,
  "git.enableCommitSigning": true,
  "git.defaultCloneDirectory": "./odoo-projects",
  "gitlens.gitCommands.skipConfirmations": [
    "fetch:command",
    "stash-push:command", 
    "branch-create:command"
  ],
  
  // ====== EXTENSION SETTINGS ======
  "extensions.allowed": {
    "*": true
  },
  
  // ====== XML CONFIGURATION ======
  "xml.format.maxLineWidth": 120,
  "xml.format.splitAttributes": true,
  "xml.validation.enabled": true,
  
  // ====== INTELLISENSE SETTINGS ======
  "editor.quickSuggestions": {
    "other": true,
    "comments": true,
    "strings": true
  },
  "editor.quickSuggestionsDelay": 10,
  "editor.suggest.localityBonus": true,
  "editor.suggest.showMethods": true,
  "editor.suggest.showFunctions": true,
  "editor.suggest.showConstructors": true,
  "editor.suggest.showFields": true,
  "editor.suggest.showVariables": true,
  "editor.suggest.showClasses": true,
  "editor.suggest.showStructs": true,
  "editor.suggest.showInterfaces": true,
  "editor.suggest.showModules": true,
  "editor.suggest.showProperties": true,
  "editor.suggest.showEvents": true,
  "editor.suggest.showOperators": true,
  "editor.suggest.showUnits": true,
  "editor.suggest.showValues": true,
  "editor.suggest.showConstants": true,
  "editor.suggest.showEnums": true,
  "editor.suggest.showEnumMembers": true,
  "editor.suggest.showKeywords": true,
  "editor.suggest.showWords": true,
  "editor.suggest.showColors": true,
  "editor.suggest.showFiles": true,
  "editor.suggest.showReferences": true,
  "editor.suggest.showCustomcolors": true,
  "editor.suggest.showFolders": true,
  "editor.suggest.showTypeParameters": true,
  "editor.suggest.showSnippets": true
}