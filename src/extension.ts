import * as vscode from 'vscode';
import { enhancePrompt } from './core/enhancer';
import { enhancePromptWithPython } from './core/pythonBridge';

const ENHANCE_COMMAND = 'contextify.enhancePrompt';

export function activate(context: vscode.ExtensionContext): void {
  const command = vscode.commands.registerCommand(ENHANCE_COMMAND, async () => {
    const editor = vscode.window.activeTextEditor;

    let sourcePrompt = '';
    let selectionToReplace: vscode.Selection | undefined;

    if (editor && !editor.selection.isEmpty) {
      sourcePrompt = editor.document.getText(editor.selection);
      selectionToReplace = editor.selection;
    } else {
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
      .get<string>('pythonPath', 'python');

    let enhanced: string;

    try {
      enhanced = await enhancePromptWithPython(sourcePrompt, {
        cwd: workspaceFolder?.uri.fsPath,
        pythonPath: configuredPython
      });
    } catch {
      enhanced = enhancePrompt(sourcePrompt);
    }

    const actions: string[] = ['Copy to clipboard', 'Cancel'];
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
    } catch {
      // Copilot may not be installed or command may be unavailable.
      // Clipboard fallback still ensures users can paste into chat manually.
    }

    void vscode.window.showInformationMessage('Enhanced prompt copied. Paste it into Copilot.');
  });

  context.subscriptions.push(command);
}

export function deactivate(): void {
  // No teardown needed for this MVP extension.
}
