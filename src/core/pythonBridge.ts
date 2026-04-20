import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface PythonEnhanceOptions {
  cwd?: string;
  pythonPath?: string;
  timeoutMs?: number;
}

export async function enhancePromptWithPython(
  input: string,
  options: PythonEnhanceOptions = {}
): Promise<string> {
  const pythonPath = options.pythonPath?.trim() || 'python';

  const { stdout } = await execFileAsync(
    pythonPath,
    ['-m', 'contextify.enhancer_bridge', input],
    {
      cwd: options.cwd,
      timeout: options.timeoutMs ?? 30000,
      windowsHide: true,
      maxBuffer: 1024 * 1024
    }
  );

  return stdout.trimEnd();
}
