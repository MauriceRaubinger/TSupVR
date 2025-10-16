using UnityEngine;
using TMPro;
using System.Collections;
using System.Diagnostics;

public class TooltipTextSetter : MonoBehaviour
{
    [SerializeField] private TextMeshPro textComponent; // World-space TextMeshPro component
    [SerializeField] private Transform backgroundTransform; // Transform of the background GameObject
    [SerializeField] private float paddingPercentageX = 1f; 
    [SerializeField] private float paddingPercentageY = 1f; 
    [SerializeField] private float maxWidth = 10f; // Maximum width for word wrapping

    private RectTransform textRectTransform; // For UI-based text
    private MeshRenderer textRenderer; // MeshRenderer for the text to access its bounds

    void Start()
    {
        // Auto-find textComponent if not assigned
        if (textComponent == null)
        {
            textComponent = GetComponentInChildren<TextMeshPro>();
        }

        // Get the MeshRenderer and RectTransform if textComponent exists
        if (textComponent != null)
        {
            textRenderer = textComponent.GetComponent<MeshRenderer>();
            textRectTransform = textComponent.GetComponent<RectTransform>();
        }
      
    }

    public void SetTooltipText(string newText)
    {
        if (textComponent == null)
        {
            UnityEngine.Debug.LogWarning("TextMeshPro component is null!");
            return;
        }

        // Update text properties
        textComponent.enableWordWrapping = true;
        textComponent.text = newText;

        // Set a reasonable width constraint for word wrapping
        if (textRectTransform != null)
        {
            textRectTransform.sizeDelta = new Vector2(maxWidth, textRectTransform.sizeDelta.y);
        }

        // Force mesh update and wait a frame for proper bounds calculation
        textComponent.ForceMeshUpdate();
        StartCoroutine(ResizeBackgroundNextFrame());
    }

    private IEnumerator ResizeBackgroundNextFrame()
    {
        // Wait one frame to ensure mesh bounds are properly calculated
        yield return null;

        ResizeBackground();
    }

    private void ResizeBackground()
    {
        if (backgroundTransform == null || textRenderer == null)
        {
            return;
        }

        // Get text bounds
        Vector3 textSize = textRenderer.bounds.size;

        // Handle edge case where bounds might be zero
        if (textSize.x <= 0 || textSize.y <= 0)
        {
            UnityEngine.Debug.LogWarning("Text bounds are zero or negative. Retrying...");
            StartCoroutine(RetryResizeBackground());
            return;
        }

        // Calculate padding based on text size (single calculation, not double)
        float actualPaddingX = textSize.x * paddingPercentageX;
        float actualPaddingY = textSize.y * paddingPercentageY;

        // Account for parent scale
        Vector3 parentScale = backgroundTransform.parent != null ?
            backgroundTransform.parent.lossyScale : Vector3.one;

        // Prevent division by zero
        if (parentScale.x == 0) parentScale.x = 1;
        if (parentScale.y == 0) parentScale.y = 1;

        // Set background size with padding (fixed the duplicate padding issue)
        backgroundTransform.localScale = new Vector3(
            (textSize.x + actualPaddingX) / parentScale.x,
            (textSize.y + actualPaddingY) / parentScale.y, // Fixed: was using paddingPercentageX
            backgroundTransform.localScale.z
        );

        UnityEngine.Debug.Log($"Text size: {textSize}, Background scale: {backgroundTransform.localScale}");
    }

    private IEnumerator RetryResizeBackground()
    {
        // Wait a bit more and try again
        yield return new WaitForSeconds(0.1f);

        textComponent.ForceMeshUpdate();
        yield return null;

        ResizeBackground();
    }

    // Optional: Method to manually trigger resize (useful for testing)
    [ContextMenu("Resize Background")]
    public void ManualResize()
    {
        if (textComponent != null)
        {
            textComponent.ForceMeshUpdate();
            StartCoroutine(ResizeBackgroundNextFrame());
        }
    }
}