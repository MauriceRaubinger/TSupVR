using System.Diagnostics;
using UnityEngine;

public class CheckMicrophones : MonoBehaviour
{
    void Start()
    {
        foreach (var device in Microphone.devices)
        {
            UnityEngine.Debug.Log($"Available Microphone: {device}");
        }
    }
}