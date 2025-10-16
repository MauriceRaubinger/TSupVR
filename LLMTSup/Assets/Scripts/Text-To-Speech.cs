using UnityEngine;
using Meta.WitAi.TTS.Utilities;
using System.Diagnostics;

public class TtsManager : MonoBehaviour
{
    [SerializeField]
    private TTSSpeaker ttsSpeaker;
    void Start()
    {
        SpeakText(" Hello, I'm Marvis your Virtual Agent, how may I help you today?");
    }

    public void SpeakText(string textToSpeak)
    {
        if (ttsSpeaker == null)
        {
            UnityEngine.Debug.LogError("TTS Speaker is not assigned!");
            return;
        }

        if (ttsSpeaker.IsSpeaking)
        {
            ttsSpeaker.Stop();
        }

        ttsSpeaker.Speak(textToSpeak);
    }
    public bool speaks()
    {
        if (ttsSpeaker != null && ttsSpeaker.IsSpeaking)
        {
            return true;
        }else
        {
            return false;
        }
    }

    public void StopCurrentSpeech()
    {
        if (ttsSpeaker != null && ttsSpeaker.IsSpeaking)
        {
            ttsSpeaker.Stop();
        }
    }
}