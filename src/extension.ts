import * as path from "path";
import {
  workspace,
  window,
  commands,
  ExtensionContext,
  TextDocument,
} from "vscode";
import { spawn, ChildProcessWithoutNullStreams } from "child_process";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

export function activate(ctx: ExtensionContext) {
  // --- 1) Launch the TSPMO Language Server ---
  const pythonPath = workspace
    .getConfiguration("tspmo")
    .get<string>("pythonPath", "python3");
  const serverModule = ctx.asAbsolutePath(
    path.join("server", "server.py")
  );

  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: [serverModule],
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "tspmo" }],
    synchronize: {
      fileEvents: workspace.createFileSystemWatcher("**/*.{tspmo,pmo}"),
    },
  };

  const client = new LanguageClient(
    "tspmoLanguageServer",
    "TSPMO Language Server",
    serverOptions,
    clientOptions
  );
  client.start();
  ctx.subscriptions.push(client);

  // --- 2) Register the "Run Current File" command ---
  const runCmd = commands.registerCommand(
    "tspmo.runCode",
    async () => {
      const editor = window.activeTextEditor;
      if (!editor) {
        window.showErrorMessage("No active editor.");
        return;
      }
      const doc: TextDocument = editor.document;
      if (doc.languageId !== "tspmo") {
        window.showErrorMessage("Not a TSPMO file.");
        return;
      }

      // Save current file so interpreter sees latest changes
      await doc.save();

      // Resolve the interpreter script path
      let interpreter = workspace
        .getConfiguration("tspmo")
        .get<string>("interpreterPath", "");
      if (!interpreter) {
        // default to the bundled interpreter in server/
        interpreter = ctx.asAbsolutePath(
          path.join("server", "interpreter.py")
        );
      } else if (!path.isAbsolute(interpreter)) {
        // resolve workspace-relative
        const ws = workspace.workspaceFolders?.[0].uri.fsPath ?? "";
        interpreter = path.join(ws, interpreter);
      }

      // The file to run
      const fileToRun = doc.uri.fsPath;

      // Create or show the output channel
      const out = window.createOutputChannel("TSPMO Run");
      out.clear();
      out.show(true);

      // Spawn the interpreter process
      const child: ChildProcessWithoutNullStreams = spawn(
        pythonPath,
        ["-W", "ignore::SyntaxWarning", interpreter, fileToRun],
        { cwd: path.dirname(fileToRun) }
      );

      child.stdout.on("data", (data: Buffer) =>
        out.append(data.toString())
      );
      child.stderr.on("data", (data: Buffer) =>
        out.append(data.toString())
      );
      child.on("close", (code: number) =>
        out.appendLine(`\n🏁 Process exited with code ${code}`)
      );
    }
  );
  ctx.subscriptions.push(runCmd);
}

// No explicit deactivate needed because the LanguageClient is pushed
// into ctx.subscriptions and will be disposed automatically.
