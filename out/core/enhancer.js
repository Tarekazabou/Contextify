"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.enhancePrompt = enhancePrompt;
/**
 * Core prompt enhancement logic shared by both CLI and VS Code extension.
 *
 * Keep this function synchronous and dependency-free so it is easy to reuse
 * in different runtimes and future integrations.
 */
function enhancePrompt(input) {
    const normalizedInput = input.trim().replace(/\s+/g, ' ');
    if (!normalizedInput) {
        return '';
    }
    return [
        'You are an expert AI programming assistant. Implement the request below with production-ready code.',
        '',
        'Request:',
        normalizedInput,
        '',
        'Constraints:',
        '- Preserve existing architecture and naming where possible.',
        '- Keep changes minimal, focused, and testable.',
        '- Include edge-case handling and clear error messages.',
        '- Return concise implementation notes and next steps.'
    ].join('\n');
}
//# sourceMappingURL=enhancer.js.map