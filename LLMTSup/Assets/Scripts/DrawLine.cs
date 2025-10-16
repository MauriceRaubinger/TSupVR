using UnityEngine;

public class DrawLine : MonoBehaviour
{
    public Transform targetObject; // Assign the target GameObject in the Inspector

    private LineRenderer lineRenderer;

    void Start()
    {
        lineRenderer = gameObject.AddComponent<LineRenderer>();
        lineRenderer.positionCount = 2;
        lineRenderer.startWidth = 0.02f; // Adjust thickness
        lineRenderer.endWidth = 0.01f;
        lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
        lineRenderer.startColor = Color.white;
        lineRenderer.endColor = Color.white;
    }

    void Update()
    {
        if (targetObject != null)
        {
            lineRenderer.SetPosition(0, transform.position); // This GameObject's position
            lineRenderer.SetPosition(1, targetObject.position); // Target GameObject's position
        }
    }
}