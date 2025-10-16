using UnityEngine;

public class InteractableIndicator : MonoBehaviour
{
    public float amplitude = 1000f; // How much the object moves up and down
    public float speed = 0.001f;       // How fast the object moves up and down
    private float startY;

    void Start()
    {
        startY = transform.position.y; // Store the initial y-position
    }

    void Update()
    {
        Vector3 pos = transform.position;
        pos.y = startY + amplitude * Mathf.Sin(speed * Time.time);
        transform.position = pos;
    }
}