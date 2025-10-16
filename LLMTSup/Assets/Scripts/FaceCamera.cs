using System.Diagnostics;
using UnityEngine;

public class FaceCamera : MonoBehaviour
{
    private Transform cameraTransform;

    void Start()
    {
        if (Camera.main != null)
        {
            cameraTransform = Camera.main.transform;
        }
        else
        {
            
        }
    }

    void Update()
    {
        if (cameraTransform != null)
        {
            Vector3 direction = cameraTransform.position - transform.position;
            direction.y = 0; // Make the direction horizontal

            if (direction != Vector3.zero)
            {
                // Calculate the target yaw (Y-axis rotation)
                float targetYaw = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;

                // Get the current Euler angles
                Vector3 currentEuler = transform.eulerAngles;

                // Set the new rotation with the same pitch (X) and roll (Z), but updated yaw (Y)
                transform.rotation = Quaternion.Euler(currentEuler.x, targetYaw, currentEuler.z);
            }
        }
    }
}