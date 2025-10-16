//Windows Speech to Text module for debugging purposes
/*using UnityEngine;
using Microsoft.MixedReality.Toolkit;
using UnityEngine.Windows.Speech; // For DictationRecognizer
using System;
using System.IO;
using System.Diagnostics;
using System.Threading.Tasks;
using static System.Net.Mime.MediaTypeNames;

public class SpeechToTextLog : MonoBehaviour
{
    private DictationRecognizer dictationRecognizer;
    private bool isListening = false;
    //private RAGCall ragScript;
    private PythonCaller pc;
    private TooltipTextSetter tt;

    void Start()
    {
        // Initialize RAGCaller
        //ragScript = GetComponent<RAGCall>();
        pc = GetComponent<PythonCaller>();
        tt = GetComponent<TooltipTextSetter>();

        // Initialize DictationRecognizer
        dictationRecognizer = new DictationRecognizer();
        if (dictationRecognizer == null)
        {
            UnityEngine.Debug.LogError("DictationRecognizer initialization failed.");
            return;
        }
        // Subscribe to dictation events
        dictationRecognizer.DictationResult += OnDictationResult;
        dictationRecognizer.DictationHypothesis += OnDictationHypothesis;
        dictationRecognizer.DictationError += OnDictationError;
        dictationRecognizer.DictationComplete += OnDictationComplete;

        // Start continuous dictation
        StartDictation();
    }

    private async void StartDictation()
    {
        if (!isListening && dictationRecognizer.Status != SpeechSystemStatus.Running)
        {
            if (PhraseRecognitionSystem.Status == SpeechSystemStatus.Running)
            {
                // Shut it down to avoid conflict with DictationRecognizer
                PhraseRecognitionSystem.Shutdown();
            }
            UnityEngine.Debug.Log("Starting continuous listening...");
            //tt.SetTooltipText("  Hello, how may I help you? :)");
            
            tt.SetTooltipText(ans);
            dictationRecognizer.Start();
            isListening = true;
        }
    }

    // Log real-time tentative results (hypothesis)
    private void OnDictationHypothesis(string text)
    {
        UnityEngine.Debug.Log($"Recognizing: {text}");
    }

    // Log final recognized text and handle async server call
    private async void OnDictationResult(string text, ConfidenceLevel confidence)
    {
        UnityEngine.Debug.Log($"Recognized: {text} (Confidence: {confidence})");

        if (confidence == ConfidenceLevel.Medium || confidence == ConfidenceLevel.High)
        {
            tt.SetTooltipText(" Thinking . . .");
            string answer = await GetAnswerFromServer(text);
            UnityEngine.Debug.Log(answer);
            if (answer != null)
            {
                tt.SetTooltipText(answer);
            }
        }
    }

    // Log errors
    private void OnDictationError(string error, int hresult)
    {
        UnityEngine.Debug.LogWarning($"Recognition faulted: {error} (HRESULT: {hresult})");
        isListening = false;
        StartDictation(); // Restart for continuous listening
    }

    // Log when dictation session ends
    private void OnDictationComplete(DictationCompletionCause cause)
    {
        UnityEngine.Debug.Log($"Dictation completed: {cause}");
        isListening = false;
        if (cause != DictationCompletionCause.Canceled)
        {
            StartDictation(); // Restart unless explicitly canceled
        }
    }

    // Stop dictation for testing
    public void StopDictation()
    {
        if (isListening && dictationRecognizer.Status == SpeechSystemStatus.Running)
        {
            dictationRecognizer.Stop();
            isListening = false;
            UnityEngine.Debug.Log("Stopped listening.");
        }
    }

    void Update()
    {
        // Stop dictation with Space key (replace with VR input later)
        if (Input.GetKeyDown(KeyCode.Space))
        {
            StopDictation();
        }
    }

    void OnDestroy()
    {
        // Clean up
        if (dictationRecognizer != null)
        {
            dictationRecognizer.DictationResult -= OnDictationResult;
            dictationRecognizer.DictationHypothesis -= OnDictationHypothesis;
            dictationRecognizer.DictationError -= OnDictationError;
            dictationRecognizer.DictationComplete -= OnDictationComplete;
            dictationRecognizer.Dispose();
            dictationRecognizer = null;
        }
    }

    public async Task<string> GetAnswerFromServer(string question)
    {
        if (pc == null)
        {
            UnityEngine.Debug.LogError("PythonCaller evades detection.");
            return null;
        }

        try
        {
            return await pc.GetAnswerAsync(question);
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError("Failure: " + e.Message);
            return null;
        }
    }
}
*/