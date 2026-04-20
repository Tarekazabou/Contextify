"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const enhancer_1 = require("./core/enhancer");
const pythonBridge_1 = require("./core/pythonBridge");
const ENHANCE_COMMAND = 'contextify.enhancePrompt';
function activate(context) {
    const command = vscode.commands.registerCommand(ENHANCE_COMMAND, async () => {
        const editor = vscode.window.activeTextEditor;
        let sourcePrompt = '';
        let selectionToReplace;
        if (editor && !editor.selection.isEmpty) {
            sourcePrompt = editor.document.getText(editor.selection);
            selectionToReplace = editor.selection;
        }
        else {
            const userInput = await vscode.window.showInputBox({
                title: 'Enhance Prompt',
                prompt: 'Enter a prompt to enhance',
                placeHolder: 'e.g. Create a reusable React modal component with keyboard support',
                ignoreFocusOut: true
            });
            if (!userInput?.trim()) {
                return;
            }
            sourcePrompt = userInput;
        }
        const workspaceFolder = editor
            ? vscode.workspace.getWorkspaceFolder(editor.document.uri)
            : vscode.workspace.workspaceFolders?.[0];
        const configuredPython = vscode.workspace
            .getConfiguration('contextify')
            .get('pythonPath', 'python');
        let enhanced;
        try {
            enhanced = await (0, pythonBridge_1.enhancePromptWithPython)(sourcePrompt, {
                cwd: workspaceFolder?.uri.fsPath,
                pythonPath: configuredPython
            });
        }
        catch {
            enhanced = (0, enhancer_1.enhancePrompt)(sourcePrompt);
        }
        const actions = ['Copy to clipboard', 'Cancel'];
        if (selectionToReplace && editor) {
            actions.unshift('Replace selection');
        }
        const action = await vscode.window.showQuickPick(actions, {
            title: 'Enhanced Prompt Ready',
            placeHolder: 'Choose what to do next',
            ignoreFocusOut: true
        });
        if (!action || action === 'Cancel') {
            return;
        }
        if (action === 'Replace selection' && selectionToReplace && editor) {
            await editor.edit((editBuilder) => {
                editBuilder.replace(selectionToReplace, enhanced);
            });
        }
        await vscode.env.clipboard.writeText(enhanced);
        try {
            await vscode.commands.executeCommand('github.copilot.chat.open');
        }
        catch {
            // Copilot may not be installed or command may be unavailable.
            // Clipboard fallback still ensures users can paste into chat manually.
        }
        void vscode.window.showInformationMessage('Enhanced prompt copied. Paste it into Copilot.');
    });
    context.subscriptions.push(command);
}
function deactivate() {
    // No teardown needed for this MVP extension.
}
//# sourceMappingURL=extension.js.map