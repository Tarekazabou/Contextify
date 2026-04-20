#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const enhancer_1 = require("../core/enhancer");
const pythonBridge_1 = require("../core/pythonBridge");
async function main() {
    const args = process.argv.slice(2);
    const input = args.join(' ').trim();
    if (!input) {
        console.error('Usage: contextify "your prompt"');
        process.exitCode = 1;
        return;
    }
    let enhanced;
    try {
        enhanced = await (0, pythonBridge_1.enhancePromptWithPython)(input, { cwd: process.cwd() });
    }
    catch {
        enhanced = (0, enhancer_1.enhancePrompt)(input);
    }
    process.stdout.write(`${enhanced}\n`);
}
void main();
//# sourceMappingURL=index.js.map