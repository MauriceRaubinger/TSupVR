//Local RAG call in Python for testing purposes
/*using UnityEngine;
using System.Diagnostics;
using System.IO;
using System.Collections;
using System.Text;
using static System.Net.Mime.MediaTypeNames;


public class RAGCall : MonoBehaviour
{
    private TooltipTextSetter tt;
    public string promptInjection;

    void Awake()
    {
        UnityEngine.Debug.Log("Initiating Python execution in background...");

        // Define paths
        string pythonPath = "python"; // Replace with full path if needed, e.g., "C:/Python39/python.exe"
        string scriptPath = UnityEngine.Application.dataPath + "/Scripts/PythonScripts/RAG_init.py";
        string docPath = UnityEngine.Application.dataPath + "/Scripts/PythonScripts/Documentation.txt";
        string question = "";
        tt = GetComponent<TooltipTextSetter>();

        // Log paths for debugging
        UnityEngine.Debug.Log($"Python script path: {scriptPath}");
        UnityEngine.Debug.Log($"Documentation path: {docPath}");

        // Validate paths
        if (!File.Exists(scriptPath))
        {
            UnityEngine.Debug.LogError($"Python script not found at: {scriptPath}");
            return;
        }
        if (!File.Exists(docPath))
        {
            UnityEngine.Debug.LogError($"Documentation.txt not found at: {docPath}");
            return;
        }

        // Start Python process asynchronously
        StartCoroutine(RunPythonScript(pythonPath, scriptPath, docPath, question));
    }
    public void PythonRAGQuery(string q)
    {
        tt.SetTooltipText("    Thinking . . . ");
        UnityEngine.Debug.Log("Initiating Python execution in background...");

        // Define paths
        string pythonPath = "python"; // Replace with full path if needed, e.g., "C:/Python39/python.exe"
        string scriptPath = UnityEngine.Application.dataPath + "/Scripts/PythonScripts/RAG_query.py";
        string docPath = UnityEngine.Application.dataPath + "/Scripts/PythonScripts/Documentation.txt";
        string question = q + "here is additional information for answering: " + promptInjection;
        promptInjection = "";

        // Log paths for debugging
        UnityEngine.Debug.Log($"Python script path: {scriptPath}");
        UnityEngine.Debug.Log($"Documentation path: {docPath}");

        // Validate paths
        if (!File.Exists(scriptPath))
        {
            UnityEngine.Debug.LogError($"Python script not found at: {scriptPath}");
            return;
        }
        if (!File.Exists(docPath))
        {
            UnityEngine.Debug.LogError($"Documentation.txt not found at: {docPath}");
            return;
        }

        // Start Python process asynchronously
        StartCoroutine(RunPythonScript(pythonPath, scriptPath, docPath, question));
    }

    private IEnumerator RunPythonScript(string pythonPath, string scriptPath, string docPath, string question)
    {
        // Configure process
        ProcessStartInfo start = new ProcessStartInfo
        {
            FileName = pythonPath,
            Arguments = $"\"{scriptPath}\" \"{question}\"",
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = false,
            CreateNoWindow = true,
            WorkingDirectory = Path.GetDirectoryName(scriptPath)
        };

        // Set environment variables
        start.EnvironmentVariables["GOOGLE_API_KEY"] = "AIzaSyCVgwFUM5ZirVMnpMf35uPvqXHULAF2mdA";
        start.EnvironmentVariables["LANGSMITH_TRACING"] = "true";
        start.EnvironmentVariables["LANGSMITH_API_KEY"] = "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";

        Process process = null;
        StringBuilder output = new StringBuilder();
        StringBuilder errors = new StringBuilder();
        int exitCode = -1;

        // Start process and set up asynchronous reading
        try
        {
            process = new Process { StartInfo = start };
            process.OutputDataReceived += (sender, e) => { if (e.Data != null) output.AppendLine(e.Data); };
            process.ErrorDataReceived += (sender, e) => { if (e.Data != null) errors.AppendLine(e.Data); };
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogError($"Failed to start Python script: {ex.Message}");
            yield break;
        }

        // Wait for process to exit without blocking Unity
        while (!process.HasExited)
        {
            yield return null; // Yield control back to Unity
        }

        // Clean up
        try
        {
            process.CancelOutputRead();
            process.CancelErrorRead();
            exitCode = process.ExitCode;
            process.Dispose();
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogError($"Error during process cleanup: {ex.Message}");
        }

        // Log results
        UnityEngine.Debug.Log($"Python process exited with code: {exitCode}");
        if (errors.Length > 0)
        {
            UnityEngine.Debug.LogError($"Python Error: {errors.ToString().Trim()}");
        }
        if (output.Length > 0)
        {
            UnityEngine.Debug.Log($"Python Output: {output.ToString().Trim()}");
            tt.SetTooltipText(output.ToString());
        }
        else
        {
            UnityEngine.Debug.Log("No output received from Python script.");
        }
    }
}*/