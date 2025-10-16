using Microsoft.MixedReality.Toolkit.UI;
using System.Diagnostics;
using System.Security.Cryptography;
using UnityEngine;

public class ObjectClickHandlerQM : MonoBehaviour
{
    private Interactable interactable;
    private PythonCaller ragCall;
    void Start()
    {
        interactable = GetComponent<Interactable>();
        interactable.OnClick.AddListener(OnClicked);
    }

    void OnClicked()
    {
        // Get the ObjectDescription component
        ObjectDescription descriptionComponent = GetComponent<ObjectDescription>();
        string description = descriptionComponent != null
            ? descriptionComponent.customDescription
            : "No description set";

        // Find the python call script 
       PythonCaller ragCall = FindObjectOfType<PythonCaller>();
        if (ragCall != null)
        {
            ragCall.promptInjection = " User clicked marker:"+description; // Set the promptInjection variable
            UnityEngine.Debug.Log($"Object '{gameObject.name}' was clicked! Set RAGCall.promptInjection to: {description}");
        }
        else
        {
            UnityEngine.Debug.LogWarning($"Object '{gameObject.name}' was clicked, but no RAGCall script was found!");
        }
        transform.gameObject.SetActive(false);
        transform.parent.GetChild(1).gameObject.SetActive(true);
    }

    private void OnDestroy()
    {
        if (interactable != null)
            interactable.OnClick.RemoveListener(OnClicked);
    }
}