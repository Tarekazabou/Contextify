#!/usr/bin/env node
import { enhancePrompt } from '../core/enhancer';
import { enhancePromptWithPython } from '../core/pythonBridge';

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const input = args.join(' ').trim();

  if (!input) {
    console.error('Usage: contextify "your prompt"');
    process.exitCode = 1;
    return;
  }

  let enhanced: string;

  try {
    enhanced = await enhancePromptWithPython(input, { cwd: process.cwd() });
  } catch {
    enhanced = enhancePrompt(input);
  }

  process.stdout.write(`${enhanced}\n`);
}

void main();
