using UnityEngine;
using Microsoft.MixedReality.Toolkit;
using Microsoft.MixedReality.Toolkit.Input;
using System.Diagnostics;
using Oculus.Voice;

public class LookDirectionTrigger : MonoBehaviour
{
    public Transform targetObject; // Object to detect gaze direction toward
    [SerializeField] private AppVoiceExperience appVoiceExperience;
    public float lookThreshold = 0.7f; // 1 = exactly forward, 0 = perpendicular
    private TooltipTextSetter tt;
    private VoiceConsoleLogger stt;
    private bool hasTriggered = false;

    void Start()
    {
        appVoiceExperience = targetObject.GetComponentInChildren<AppVoiceExperience>();
        tt = targetObject.GetComponent<TooltipTextSetter>();
        stt = targetObject.GetComponentInChildren<VoiceConsoleLogger>();
    }

    void Update()
    {
        // Get the gaze forward direction (head-based)
        var gazeDirection = CoreServices.InputSystem.GazeProvider.GazeDirection;

        // Vector from gaze origin to target
        var toTarget = (targetObject.position - CoreServices.InputSystem.GazeProvider.GazeOrigin).normalized;

        // Dot product tells how aligned the gaze and target direction are
        float alignment = Vector3.Dot(gazeDirection.normalized, toTarget);

        // Check if user is looking close enough to target direction
        if (alignment > lookThreshold)
        {
                if (!appVoiceExperience.Active && stt.processing ==false)
                {
                    appVoiceExperience.Activate();
                UnityEngine.Debug.Log("Activated");
                }

        }
    }



}
