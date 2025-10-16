using Microsoft.MixedReality.Toolkit.UI;
using System.Diagnostics;
using UnityEngine;
using TMPro;

public class ObjectClickHandlerEM : MonoBehaviour
{
    private Interactable interactable;
    private PythonCaller ragCall;
    [SerializeField] private TextMeshPro textComponent;

    void Start()
    {
        if (textComponent == null)
        {
            textComponent = GetComponentInChildren<TextMeshPro>();
        }
        interactable = GetComponent<Interactable>();
        interactable.OnClick.AddListener(OnClicked);
        UnityEngine.Debug.Log(textComponent.text);
        if (transform.parent != null && transform.parent.childCount > 0)
        {
            
            Transform firstChild = transform.parent.parent.GetChild(0);
            ObjectDescription objDesc = firstChild.GetComponent<ObjectDescription>();
      

            if (objDesc != null)
            {
                // Access the string

                string description = objDesc.customDescription;
                textComponent.enableWordWrapping = true;
                textComponent.text = description;
                textComponent.ForceMeshUpdate();
            }
            else
            {
                UnityEngine.Debug.LogWarning("ObjectDescription component not found on first child!");
            }
        }
        else
        {
            UnityEngine.Debug.LogWarning("Parent is null or has no children!");
        }
    }


    void OnClicked()
    {
        UnityEngine.Debug.Log($"Object was clicked!");
        // Get the ObjectDescription component
        // Find the python call script 
        PythonCaller ragCall = FindObjectOfType<PythonCaller>();
        if (ragCall != null)
        {
            //ragCall.promptInjection = ""; // Set the promptInjection variable
            UnityEngine.Debug.Log($"Object '{gameObject.name}' was clicked!");
        }
        else
        {
            UnityEngine.Debug.LogWarning($"Object '{gameObject.name}' was clicked, but no RAGCall script was found!");
        }
        transform.parent.parent.GetChild(0).gameObject.SetActive(true);
        transform.parent.gameObject.SetActive(false);
    }

    private void OnDestroy()
    {
        if (interactable != null)
            interactable.OnClick.RemoveListener(OnClicked);
    }
}