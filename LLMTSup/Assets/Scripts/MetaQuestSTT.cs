using UnityEngine;
using Meta.WitAi;
using Meta.WitAi.Events;
using Meta.WitAi.Interfaces;
using Oculus.Voice;
using System.Threading.Tasks;
using System.Diagnostics;
using System;
using System.Reflection;

public class VoiceConsoleLogger : MonoBehaviour
{
    [SerializeField] private AppVoiceExperience appVoiceExperience;
    [SerializeField] private Transform machine;
    [SerializeField] private GameObject wp;
    [SerializeField] private ObjectRestorer objectToRestore;
    private TtsManager ttsManager;
    private PythonCaller pc;
    private TooltipTextSetter tt;
    public bool processing = false;

    private void OnEnable()
    {
        // MODIFIED: Automatically find the TtsManager component on this same GameObject
        ttsManager = GetComponent<TtsManager>();
        appVoiceExperience = GetComponent<AppVoiceExperience>();
        pc = GetComponent<PythonCaller>();
        tt = GetComponentInParent<TooltipTextSetter>();

        if (appVoiceExperience == null)
        {
            UnityEngine.Debug.LogError("AppVoiceExperience not assigned!");
            return;
        }
        if (ttsManager == null)
        {
            UnityEngine.Debug.LogError("TtsManager component not found on the same GameObject!");
        }

        appVoiceExperience.VoiceEvents.OnPartialTranscription.AddListener(OnPartialTranscription);
        appVoiceExperience.VoiceEvents.OnFullTranscription.AddListener(OnFullTranscription);

        SetAndSpeakResponse("Hello, how may I help you?");
        appVoiceExperience.Activate();
    }

    // ... the rest of your script remains exactly the same ...

    private void OnDisable()
    {
        if (appVoiceExperience == null) return;
        appVoiceExperience.VoiceEvents.OnPartialTranscription.RemoveListener(OnPartialTranscription);
        appVoiceExperience.VoiceEvents.OnFullTranscription.RemoveListener(OnFullTranscription);
    }

    private void SetAndSpeakResponse(string text)
    {
        if (tt != null)
        {
            tt.SetTooltipText(text);
        }
        if (ttsManager != null)
        {
            ttsManager.SpeakText(text);
        }
    }

    private void OnPartialTranscription(string transcription)
    {
        UnityEngine.Debug.Log($"Partial: {transcription}");

        if (ttsManager != null)
        {
            if (ttsManager.speaks()) pc.promptInjection += " System /You got interrupted while speaking./";
            ttsManager.StopCurrentSpeech();
        }

        tt.SetTooltipText("Listening . . .");
    }

    private async void OnFullTranscription(string transcription)
    {
        UnityEngine.Debug.Log($"Final: {transcription}");
        processing = true;
        string ans = await GetAnswerFromServer(transcription);
        string prefix = "passcode12345";
        string prefix2 = "passcode69420";
        string prefix3 = "passcode66666";

        if (ans.StartsWith(prefix))
        {
            string remainder = ans.Substring(prefix.Length).Trim();
            switch (remainder.ToLower())
            {
                case "lift up":
                    SetAndSpeakResponse("I lifted the object up");
                    machine.transform.position += Vector3.up * 2f;
                    if (wp != null)
                    {
                        wp.SetActive(false);
                    }
                    break;
                case "bring down":
                    SetAndSpeakResponse("I brought the object down");
                    Vector3 newPosition = machine.transform.position + Vector3.down * 2f;
                    newPosition.y = Mathf.Max(newPosition.y, 0f);
                    machine.transform.position = newPosition;
                    if (wp != null)
                    {
                        wp.SetActive(false);
                    }
                    break;
                case "rotate":
                    SetAndSpeakResponse("I rotated the object");
                    if (Camera.main != null)
                    {
                        Vector3 directionToCamera = Camera.main.transform.position - machine.transform.position;
                        directionToCamera.y = 0;
                        float yRotation = Mathf.Atan2(directionToCamera.x, directionToCamera.z) * Mathf.Rad2Deg;
                        machine.transform.rotation = Quaternion.Euler(machine.transform.rotation.eulerAngles.x, yRotation, machine.transform.rotation.eulerAngles.z);
                    }
                    break;
                default:
                    SetAndSpeakResponse("I'm sorry, I couldn't execute your command.");
                    break;
            }
        }
        else if (ans.StartsWith(prefix2))
        {
            string remainder = ans.Substring(prefix2.Length).Trim();
            switch (remainder.ToLower())
            {
                case "engine":
                    SetAndSpeakResponse("Changed object to engine");
                    //machine = engine;
                    break;
                case "reactor":
                    SetAndSpeakResponse("Changed object to reactor");
                    //machine = reactor;
                    break;
                default:
                    SetAndSpeakResponse("I'm sorry, I couldn't identify that object.");
                    break;
            }
        }
        else if (ans.StartsWith(prefix3))
        {
            SetAndSpeakResponse("I restored the origínal state.");
            if (wp != null)
            {
                    wp.SetActive(true);
                    if (objectToRestore != null)
                    {
                        objectToRestore.ResetObjectState();
                    }
            }
        }
        else
        {
            SetAndSpeakResponse(ans);
        }
        pc.promptInjection = "";
        appVoiceExperience.Activate();
        processing = false;
    }

    public async Task<string> GetAnswerFromServer(string question)
    {
        if (pc == null)
        {
            UnityEngine.Debug.LogError("PythonCaller evades detection.");
            return "Python Caller not found.";
        }
        try
        {
            return await pc.GetAnswerAsync(question);
        }
        catch (System.Exception e)
        {
            SetAndSpeakResponse("I'm sorry, I couldn't establish a connection.");
            UnityEngine.Debug.LogError("Failure: " + e.Message);
            return null;
        }
    }
}