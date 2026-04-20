"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.enhancePromptWithPython = enhancePromptWithPython;
const child_process_1 = require("child_process");
const util_1 = require("util");
const execFileAsync = (0, util_1.promisify)(child_process_1.execFile);
async function enhancePromptWithPython(input, options = {}) {
    const pythonPath = options.pythonPath?.trim() || 'python';
    const { stdout } = await execFileAsync(pythonPath, ['-m', 'contextify.enhancer_bridge', input], {
        cwd: options.cwd,
        timeout: options.timeoutMs ?? 30000,
        windowsHide: true,
        maxBuffer: 1024 * 1024
    });
    return stdout.trimEnd();
}
//# sourceMappingURL=pythonBridge.js.map