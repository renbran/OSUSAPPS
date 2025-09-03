[
  // ====== SPEC WORKFLOW SHORTCUTS ======
  {
    "key": "ctrl+alt+spec",
    "command": "github.copilot.chat.ask",
    "args": "@spec start spec workflow for new feature"
  },
  {
    "key": "ctrl+alt+req",
    "command": "github.copilot.chat.ask", 
    "args": "@requirements create EARS requirements document"
  },
  {
    "key": "ctrl+alt+des",
    "command": "github.copilot.chat.ask",
    "args": "@design create design document with architecture diagrams"
  },
  {
    "key": "ctrl+alt+val",
    "command": "github.copilot.chat.ask",
    "args": "@spec validate requirements and design documents"
  },
  {
    "key": "ctrl+alt+ears",
    "command": "github.copilot.chat.ask",
    "args": "@requirements convert this to EARS format (WHEN/IF + SHALL)"
  },
  
  // ====== COPILOT CHAT SHORTCUTS ======
  {
    "key": "ctrl+shift+i",
    "command": "github.copilot.chat.explain",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+r", 
    "command": "github.copilot.chat.review",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+f",
    "command": "github.copilot.chat.fix", 
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+t",
    "command": "github.copilot.chat.tests",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+d",
    "command": "github.copilot.chat.docs",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+o",
    "command": "github.copilot.chat.optimize",
    "when": "editorTextFocus"
  },
  
  // ====== INLINE SUGGESTIONS ======
  {
    "key": "alt+\\",
    "command": "editor.action.inlineSuggest.trigger",
    "when": "editorTextFocus && !editorReadonly"
  },
  {
    "key": "alt+]",
    "command": "editor.action.inlineSuggest.showNext",
    "when": "inlineSuggestionsVisible"
  },
  {
    "key": "alt+[", 
    "command": "editor.action.inlineSuggest.showPrevious",
    "when": "inlineSuggestionsVisible"
  },
  {
    "key": "ctrl+alt+enter",
    "command": "editor.action.inlineSuggest.accept",
    "when": "inlineSuggestionsVisible"
  },
  {
    "key": "ctrl+alt+right",
    "command": "editor.action.inlineSuggest.acceptNextWord",
    "when": "inlineSuggestionsVisible"
  },
  {
    "key": "escape",
    "command": "editor.action.inlineSuggest.hide",
    "when": "inlineSuggestionsVisible"
  },
  
  // ====== COPILOT PANEL MANAGEMENT ======
  {
    "key": "ctrl+shift+c",
    "command": "workbench.panel.chat.view.copilot.focus"
  },
  {
    "key": "ctrl+alt+c",
    "command": "github.copilot.chat.newChat"
  },
  {
    "key": "ctrl+alt+shift+c",
    "command": "github.copilot.chat.clear"
  },
  
  // ====== ODOO-SPECIFIC SHORTCUTS ======
  {
    "key": "ctrl+alt+m",
    "command": "github.copilot.chat.ask",
    "args": "@odoo create a new Odoo 17 model with security and views based on approved design"
  },
  {
    "key": "ctrl+alt+v", 
    "command": "github.copilot.chat.ask",
    "args": "@odoo create Odoo 17 views for the selected model following design specifications"
  },
  {
    "key": "ctrl+alt+s",
    "command": "github.copilot.chat.ask", 
    "args": "@odoo generate security rules and access rights for this model per design"
  },
  {
    "key": "ctrl+alt+w",
    "command": "github.copilot.chat.ask",
    "args": "@odoo create a wizard for this functionality following Odoo 17 patterns"
  },
  {
    "key": "ctrl+alt+p",
    "command": "github.copilot.chat.ask",
    "args": "@odoo optimize this code for performance and avoid N+1 queries"
  },
  {
    "key": "ctrl+alt+mod",
    "command": "github.copilot.chat.ask",
    "args": "@odoo create complete Odoo 17 module from approved spec documents"
  },
  
  // ====== DOCUMENTATION SHORTCUTS ======
  {
    "key": "ctrl+alt+doc",
    "command": "github.copilot.chat.ask",
    "args": "Generate comprehensive documentation for this code including docstrings and architecture notes"
  },
  {
    "key": "ctrl+alt+arch",
    "command": "github.copilot.chat.ask",
    "args": "@design create architecture diagram using Mermaid for this component"
  },
  {
    "key": "ctrl+alt+flow",
    "command": "github.copilot.chat.ask",
    "args": "@design create data flow diagram using Mermaid for this process"
  },
  
  // ====== TESTING SHORTCUTS ======
  {
    "key": "ctrl+alt+test",
    "command": "github.copilot.chat.ask",
    "args": "Create comprehensive unit tests that validate EARS requirements for this code"
  },
  {
    "key": "ctrl+alt+int",
    "command": "github.copilot.chat.ask",
    "args": "Create integration tests for this workflow following the design specifications"
  },
  
  // ====== CODE GENERATION SHORTCUTS ======
  {
    "key": "ctrl+shift+g",
    "command": "github.copilot.generate"
  },
  {
    "key": "ctrl+shift+a",
    "command": "editor.action.autoFix",
    "when": "editorTextFocus && !editorReadonly"
  },
  {
    "key": "ctrl+shift+space",
    "command": "editor.action.triggerSuggest",
    "when": "editorHasCompletionItemProvider && textInputFocus && !editorReadonly"
  },
  
  // ====== WORKFLOW VALIDATION SHORTCUTS ======
  {
    "key": "ctrl+alt+check",
    "command": "github.copilot.chat.ask",
    "args": "Check if this implementation matches the approved requirements and design"
  },
  {
    "key": "ctrl+alt+trace",
    "command": "github.copilot.chat.ask",
    "args": "Trace this code back to specific EARS requirements and design components"
  },
  
  // ====== MULTI-CURSOR COPILOT ======
  {
    "key": "ctrl+alt+down",
    "command": "editor.action.insertCursorBelow",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+up", 
    "command": "editor.action.insertCursorAbove",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+l",
    "command": "editor.action.selectHighlights",
    "when": "editorFocus"
  }
]